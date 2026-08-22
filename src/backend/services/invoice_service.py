import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from src.backend.core.config import settings
from src.backend.db.repositories.invoice_repo import (
    create_invoice,
    generate_invoice_number,
    get_invoice_with_items,
    list_invoices,
    soft_delete_invoice,
    update_invoice_status,
)
from src.backend.models.time_tracking import TimeEntry


def _compute_totals(
    items_data: list[dict[str, Any]], tax_rate: Decimal
) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
    subtotal = sum(
        (Decimal(str(item["quantity"])) * Decimal(str(item["rate"])) for item in items_data),
        Decimal("0"),
    )
    gst_percent = tax_rate
    gst_amount = (subtotal * gst_percent / Decimal("100")).quantize(Decimal("0.01"))
    tax_amount = gst_amount
    total = subtotal + gst_amount
    return subtotal, tax_amount, total, gst_percent, gst_amount


def _invoice_to_read(invoice: Any, db: Session) -> dict[str, Any]:
    from src.backend.models.project import Project
    from src.backend.models.user import User

    project = db.query(Project).filter(Project.id == invoice.project_id).first()
    user = db.query(User).filter(User.id == invoice.created_by).first()

    items = []
    for item in invoice.items:
        items.append(
            {
                "id": item.id,
                "invoice_id": item.invoice_id,
                "description": item.description,
                "quantity": item.quantity,
                "rate": item.rate,
                "amount": item.amount,
                "category": item.category,
                "time_entry_id": item.time_entry_id,
                "created_at": item.created_at,
            }
        )

    return {
        "id": invoice.id,
        "project_id": invoice.project_id,
        "invoice_number": invoice.invoice_number,
        "status": invoice.status,
        "subtotal": invoice.subtotal,
        "tax_rate": invoice.tax_rate,
        "tax_amount": invoice.tax_amount,
        "gst_percent": invoice.gst_percent,
        "gst_amount": invoice.gst_amount,
        "total": invoice.total,
        "currency": invoice.currency,
        "due_date": invoice.due_date,
        "notes": invoice.notes,
        "created_by": invoice.created_by,
        "paid_at": invoice.paid_at,
        "created_at": invoice.created_at,
        "items": items,
        "project_name": project.name if project else None,
        "created_by_name": user.name if user else None,
    }


def create_invoice_service(
    db: Session,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    due_date: date | None,
    notes: str | None,
    tax_rate: Decimal,
    items_data: list[dict[str, Any]],
) -> dict[str, Any]:
    invoice_number = generate_invoice_number(db)

    for item in items_data:
        if "amount" not in item:
            item["amount"] = Decimal(str(item["quantity"])) * Decimal(str(item["rate"]))

    subtotal, tax_amount, total, gst_percent, gst_amount = _compute_totals(items_data, tax_rate)

    invoice_data = {
        "project_id": project_id,
        "invoice_number": invoice_number,
        "status": "draft",
        "subtotal": subtotal,
        "tax_rate": tax_rate,
        "tax_amount": tax_amount,
        "gst_percent": gst_percent,
        "gst_amount": gst_amount,
        "total": total,
        "currency": "INR",
        "due_date": due_date,
        "notes": notes,
        "created_by": user_id,
    }

    invoice = create_invoice(db, invoice_data, items_data)
    return _invoice_to_read(invoice, db)


def generate_from_time_entries(
    db: Session,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    start_date: date,
    end_date: date,
) -> dict[str, Any]:
    entries = (
        db.query(TimeEntry)
        .filter(
            TimeEntry.project_id == project_id,
            TimeEntry.date >= start_date,
            TimeEntry.date <= end_date,
            TimeEntry.is_billable.is_(True),
            TimeEntry.deleted_at.is_(None),
        )
        .all()
    )

    if not entries:
        raise ValueError("No billable time entries found for the given date range")

    # Rate from settings (DEFAULT_HOURLY_RATE_INR), not a silent magic number in logic.
    rate_per_hour = Decimal(settings.DEFAULT_HOURLY_RATE_INR)
    tax_rate = Decimal("18.00")  # GST % — invoice-level default; configurable later

    items_data: list[dict[str, Any]] = []
    for entry in entries:
        amount = entry.hours * rate_per_hour
        items_data.append(
            {
                "description": f"Services — {entry.hours}h @ {rate_per_hour}/h",
                "quantity": entry.hours,
                "rate": rate_per_hour,
                "amount": amount,
                "category": "time",
                "time_entry_id": entry.id,
            }
        )

    return create_invoice_service(
        db,
        project_id=project_id,
        user_id=user_id,
        due_date=None,
        notes=f"Invoice for period {start_date} to {end_date}",
        tax_rate=tax_rate,
        items_data=items_data,
    )


def update_invoice_status_service(
    db: Session,
    invoice_id: uuid.UUID,
    new_status: str,
) -> dict[str, Any]:
    invoice = get_invoice_with_items(db, invoice_id)
    if not invoice:
        raise ValueError("Invoice not found")

    valid_transitions = {
        "draft": ["sent"],
        "sent": ["paid"],
    }

    allowed = valid_transitions.get(invoice.status, [])
    if new_status not in allowed:
        raise ValueError(
            f"Cannot transition from '{invoice.status}' to '{new_status}'. " f"Allowed: {allowed}"
        )

    paid_at = datetime.now(tz=UTC) if new_status == "paid" else None
    updated = update_invoice_status(db, invoice_id, new_status, paid_at=paid_at)
    return _invoice_to_read(updated, db)


def delete_invoice_service(db: Session, invoice_id: uuid.UUID) -> bool:
    invoice = get_invoice_with_items(db, invoice_id)
    if not invoice:
        raise ValueError("Invoice not found")
    if invoice.status != "draft":
        raise ValueError("Only draft invoices can be deleted")
    return soft_delete_invoice(db, invoice_id)


def get_invoice_service(db: Session, invoice_id: uuid.UUID) -> dict[str, Any] | None:
    invoice = get_invoice_with_items(db, invoice_id)
    if not invoice:
        return None
    return _invoice_to_read(invoice, db)


def list_invoices_service(
    db: Session,
    project_id: uuid.UUID,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict[str, Any]], int, int, int]:
    items, total, pg, ps = list_invoices(
        db, project_id, status=status, page=page, page_size=page_size
    )
    return [_invoice_to_read(i, db) for i in items], total, pg, ps
