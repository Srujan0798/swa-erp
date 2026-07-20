import uuid
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from sqlalchemy.orm import Session

from src.backend.core.quote_workflow import can_transition, get_allowed_transitions
from src.backend.db.repositories.audit_repo import create_entry
from src.backend.db.repositories.boq_repo import get_by_id as get_boq_by_id
from src.backend.db.repositories.client_repo import get_by_id as get_client_by_id
from src.backend.db.repositories.project_repo import get_by_id as get_project_by_id
from src.backend.db.repositories.quote_repo import (
    clone_quote,
    create_quote,
    get_by_id,
    get_with_items,
    list_by_project,
    replace_items,
    soft_delete,
    update_status,
)
from src.backend.db.repositories.user_repo import get_by_id as get_user_by_id


def _record_event(
    db: Session,
    action: str,
    user_id: uuid.UUID | None,
    entity_id: uuid.UUID,
    before_json: dict | None = None,
    after_json: dict | None = None,
) -> None:
    create_entry(
        db,
        action=action,
        entity_type="quote",
        user_id=user_id,
        entity_id=entity_id,
        before_json=before_json,
        after_json=after_json,
    )


def _quote_to_enriched_dict(quote: Any, db: Session) -> dict[str, Any]:
    creator = get_user_by_id(db, quote.created_by) if quote.created_by else None
    approver = get_user_by_id(db, quote.approved_by) if quote.approved_by else None
    project = get_project_by_id(db, quote.project_id)
    client_name = None
    if project and project.client_id:
        client = get_client_by_id(db, project.client_id)
        client_name = client.name if client else None

    return {
        "id": quote.id,
        "project_id": quote.project_id,
        "boq_id": quote.boq_id,
        "version_number": quote.version_number,
        "status": quote.status,
        "subtotal": quote.subtotal,
        "markup_percent": quote.markup_percent,
        "markup_amount": quote.markup_amount,
        "tax_percent": quote.tax_percent,
        "tax_amount": quote.tax_amount,
        "total_amount": quote.total_amount,
        "terms": quote.terms,
        "validity_days": quote.validity_days,
        "valid_until": quote.valid_until,
        "created_by": quote.created_by,
        "approved_by": quote.approved_by,
        "approved_at": quote.approved_at,
        "sent_at": quote.sent_at,
        "client_response": quote.client_response,
        "client_response_at": quote.client_response_at,
        "client_response_notes": quote.client_response_notes,
        "created_at": quote.created_at,
        "updated_at": quote.updated_at,
        "items": [
            {
                "id": item.id,
                "quote_id": item.quote_id,
                "boq_item_id": item.boq_item_id,
                "line_number": item.line_number,
                "category": item.category,
                "description": item.description,
                "specification": item.specification,
                "unit": item.unit,
                "quantity": item.quantity,
                "rate": item.rate,
                "amount": item.amount,
            }
            for item in quote.items
        ],
        "creator_name": creator.name if creator else None,
        "approver_name": approver.name if approver else None,
        "project_name": project.name if project else None,
        "client_name": client_name,
    }


def _recalculate_totals(quote: Any) -> None:
    quote.subtotal = sum(item.amount for item in quote.items)
    quote.markup_amount = (quote.subtotal * quote.markup_percent / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    quote.tax_amount = (
        (quote.subtotal + quote.markup_amount) * quote.tax_percent / Decimal("100")
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    quote.total_amount = (quote.subtotal + quote.markup_amount + quote.tax_amount).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def _transition(
    db: Session, quote_id: uuid.UUID, to_status: str, actor_id: uuid.UUID, **kwargs: Any
) -> dict[str, Any]:
    quote = get_by_id(db, quote_id)
    if not quote:
        raise ValueError("Quote not found")
    if not can_transition(quote.status, to_status):
        allowed = get_allowed_transitions(quote.status)
        raise ValueError(
            f"Cannot transition from '{quote.status}' to '{to_status}'. Allowed: {allowed}"
        )

    before_status = quote.status
    updated = update_status(db, quote_id, to_status, **kwargs)
    if not updated:
        raise ValueError("Failed to update quote status")

    _record_event(
        db,
        action=f"quote.transition.{to_status}",
        user_id=actor_id,
        entity_id=quote_id,
        before_json={"status": before_status},
        after_json={"status": to_status},
    )

    return _quote_to_enriched_dict(updated, db)


def generate_quote(
    db: Session,
    project_id: uuid.UUID,
    boq_id: uuid.UUID,
    markup_percent: Decimal = Decimal("0"),
    tax_percent: Decimal = Decimal("18"),
    terms: str | None = None,
    validity_days: int = 30,
    created_by: uuid.UUID | None = None,
) -> dict[str, Any]:
    from src.backend.models.boq import BOQItem

    boq = get_boq_by_id(db, boq_id)
    if not boq:
        raise ValueError("BOQ not found")
    if boq.project_id != project_id:
        raise ValueError("BOQ does not belong to this project")

    boq_items = db.query(BOQItem).filter(BOQItem.boq_id == boq_id).order_by(BOQItem.line_number).all()

    items_data = []
    for boq_item in boq_items:
        amount = (boq_item.quantity * boq_item.rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        items_data.append(
            {
                "boq_item_id": boq_item.id,
                "line_number": boq_item.line_number,
                "category": boq_item.category,
                "description": boq_item.description,
                "specification": boq_item.specification,
                "unit": boq_item.unit,
                "quantity": boq_item.quantity,
                "rate": boq_item.rate,
                "amount": amount,
            }
        )

    subtotal = sum((i["amount"] for i in items_data), Decimal("0"))
    markup_amount = (subtotal * markup_percent / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    tax_amount = ((subtotal + markup_amount) * tax_percent / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    total_amount = (subtotal + markup_amount + tax_amount).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    quote_data = {
        "project_id": project_id,
        "boq_id": boq_id,
        "version_number": boq.version_number,
        "status": "draft",
        "subtotal": subtotal,
        "markup_percent": markup_percent,
        "markup_amount": markup_amount,
        "tax_percent": tax_percent,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
        "terms": terms,
        "validity_days": validity_days,
        "valid_until": date.today() + timedelta(days=validity_days),
        "created_by": created_by,
    }

    quote = create_quote(db, quote_data, items_data)

    _record_event(
        db,
        action="quote.create",
        user_id=created_by,
        entity_id=quote.id,
        after_json={"status": "draft", "total_amount": str(total_amount)},
    )

    return _quote_to_enriched_dict(quote, db)


def get_quote(db: Session, quote_id: uuid.UUID) -> dict[str, Any] | None:
    quote = get_with_items(db, quote_id)
    if not quote:
        return None
    return _quote_to_enriched_dict(quote, db)


def list_quotes(
    db: Session, project_id: uuid.UUID, page: int = 1, page_size: int = 20
) -> tuple[list[dict[str, Any]], int, int, int]:
    quotes, total, pg, ps = list_by_project(db, project_id, page, page_size)
    return [_quote_to_enriched_dict(q, db) for q in quotes], total, pg, ps


def update_quote_service(
    db: Session, quote_id: uuid.UUID, data: dict[str, Any], actor_id: uuid.UUID
) -> dict[str, Any]:
    quote = get_with_items(db, quote_id)
    if not quote:
        raise ValueError("Quote not found")
    if quote.status != "draft":
        raise ValueError("Can only update quotes in draft status")

    before = _quote_to_enriched_dict(quote, db)

    if "markup_percent" in data and data["markup_percent"] is not None:
        quote.markup_percent = data["markup_percent"]
    if "tax_percent" in data and data["tax_percent"] is not None:
        quote.tax_percent = data["tax_percent"]
    if "validity_days" in data and data["validity_days"] is not None:
        quote.validity_days = data["validity_days"]
        quote.valid_until = date.today() + timedelta(days=data["validity_days"])
    if "terms" in data:
        quote.terms = data["terms"]

    if "items" in data and data["items"] is not None:
        replace_items(db, quote_id, data["items"])
        quote = get_with_items(db, quote_id)

    _recalculate_totals(quote)
    db.commit()
    db.refresh(quote)

    _record_event(
        db,
        action="quote.update",
        user_id=actor_id,
        entity_id=quote_id,
        before_json={"status": before["status"]},
        after_json={"status": quote.status},
    )

    return _quote_to_enriched_dict(quote, db)


def delete_quote_service(db: Session, quote_id: uuid.UUID, actor_id: uuid.UUID) -> bool:
    quote = get_by_id(db, quote_id)
    if not quote:
        return False

    _record_event(
        db,
        action="quote.delete",
        user_id=actor_id,
        entity_id=quote_id,
        before_json={"status": quote.status},
    )

    return soft_delete(db, quote_id)


def submit_quote(db: Session, quote_id: uuid.UUID, actor_id: uuid.UUID) -> dict[str, Any]:
    return _transition(db, quote_id, "pending_approval", actor_id)


def approve_quote(db: Session, quote_id: uuid.UUID, actor_id: uuid.UUID) -> dict[str, Any]:
    from datetime import datetime as dt

    return _transition(db, quote_id, "approved", actor_id, approved_by=actor_id, approved_at=dt.utcnow())


def send_quote(db: Session, quote_id: uuid.UUID, actor_id: uuid.UUID) -> dict[str, Any]:
    from datetime import datetime as dt

    return _transition(db, quote_id, "sent", actor_id, sent_at=dt.utcnow())


def respond_quote(
    db: Session, quote_id: uuid.UUID, response: str, notes: str | None, actor_id: uuid.UUID
) -> dict[str, Any]:
    from datetime import datetime as dt

    if response not in ("accepted", "rejected"):
        raise ValueError("Response must be 'accepted' or 'rejected'")

    return _transition(
        db,
        quote_id,
        response,
        actor_id,
        client_response=response,
        client_response_at=dt.utcnow(),
        client_response_notes=notes,
    )


def clone_to_draft(db: Session, quote_id: uuid.UUID, actor_id: uuid.UUID) -> dict[str, Any]:
    quote = get_with_items(db, quote_id)
    if not quote:
        raise ValueError("Quote not found")
    if quote.status != "rejected":
        raise ValueError("Can only clone rejected quotes")

    new_quote_id = uuid.uuid4()
    cloned = clone_quote(db, quote_id, new_quote_id)
    if not cloned:
        raise ValueError("Failed to clone quote")

    _record_event(
        db,
        action="quote.clone",
        user_id=actor_id,
        entity_id=cloned.id,
        before_json={"cloned_from": str(quote_id)},
        after_json={"status": "draft"},
    )

    return _quote_to_enriched_dict(cloned, db)
