import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from src.backend.models.quote import Quote, QuoteItem


def create_quote(db: Session, data: dict[str, Any], items: list[dict[str, Any]]) -> Quote:
    quote = Quote(**data)
    db.add(quote)
    db.flush()
    for item_data in items:
        item_data["quote_id"] = quote.id
        item = QuoteItem(**item_data)
        db.add(item)
    db.commit()
    db.refresh(quote)
    return quote


def get_by_id(db: Session, quote_id: uuid.UUID) -> Quote | None:
    return db.query(Quote).filter(
        Quote.id == quote_id,
        Quote.deleted_at.is_(None),
    ).first()


def get_with_items(db: Session, quote_id: uuid.UUID) -> Quote | None:
    quote = get_by_id(db, quote_id)
    if quote:
        _ = quote.items  # trigger lazy load
    return quote


def list_by_project(
    db: Session, project_id: uuid.UUID, page: int = 1, page_size: int = 20
) -> tuple[list[Quote], int, int, int]:
    query = db.query(Quote).filter(
        Quote.project_id == project_id,
        Quote.deleted_at.is_(None),
    )
    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Quote.created_at.desc()).offset(offset).limit(page_size).all()
    return items, total, page, page_size


def update_quote(db: Session, quote_id: uuid.UUID, data: dict[str, Any]) -> Quote | None:
    quote = get_by_id(db, quote_id)
    if not quote:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(quote, key, value)
    db.commit()
    db.refresh(quote)
    return quote


def update_status(db: Session, quote_id: uuid.UUID, status: str, **kwargs: Any) -> Quote | None:
    quote = get_by_id(db, quote_id)
    if not quote:
        return None
    quote.status = status
    for key, value in kwargs.items():
        if value is not None:
            setattr(quote, key, value)
    db.commit()
    db.refresh(quote)
    return quote


def soft_delete(db: Session, quote_id: uuid.UUID) -> bool:
    quote = get_by_id(db, quote_id)
    if not quote:
        return False
    quote.deleted_at = datetime.utcnow()
    db.commit()
    return True


def replace_items(db: Session, quote_id: uuid.UUID, items: list[dict[str, Any]]) -> None:
    db.query(QuoteItem).filter(QuoteItem.quote_id == quote_id).delete()
    for item_data in items:
        item_data["quote_id"] = quote_id
        item = QuoteItem(**item_data)
        db.add(item)
    db.commit()


def clone_quote(db: Session, source_quote_id: uuid.UUID, new_quote_id: uuid.UUID) -> Quote | None:
    source = get_with_items(db, source_quote_id)
    if not source:
        return None

    cloned = Quote(
        id=new_quote_id,
        project_id=source.project_id,
        boq_id=source.boq_id,
        version_number=source.version_number,
        status="draft",
        subtotal=source.subtotal,
        markup_percent=source.markup_percent,
        markup_amount=source.markup_amount,
        tax_percent=source.tax_percent,
        tax_amount=source.tax_amount,
        total_amount=source.total_amount,
        terms=source.terms,
        validity_days=source.validity_days,
        valid_until=source.valid_until,
        created_by=source.created_by,
    )
    db.add(cloned)
    db.flush()

    for item in source.items:
        cloned_item = QuoteItem(
            quote_id=new_quote_id,
            boq_item_id=item.boq_item_id,
            line_number=item.line_number,
            category=item.category,
            description=item.description,
            specification=item.specification,
            unit=item.unit,
            quantity=item.quantity,
            rate=item.rate,
            amount=item.amount,
        )
        db.add(cloned_item)

    db.commit()
    db.refresh(cloned)
    return cloned
