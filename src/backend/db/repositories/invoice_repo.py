import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.backend.models.invoice import Invoice, InvoiceItem


def create_invoice(
    db: Session,
    data: dict[str, Any],
    items_data: list[dict[str, Any]],
) -> Invoice:
    invoice = Invoice(**data)
    db.add(invoice)
    db.flush()
    for item_data in items_data:
        item_data["invoice_id"] = invoice.id
        item = InvoiceItem(**item_data)
        db.add(item)
    db.commit()
    db.refresh(invoice)
    return invoice


def get_invoice_by_id(db: Session, invoice_id: uuid.UUID) -> Invoice | None:
    return db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.deleted_at.is_(None),
    ).first()


def get_invoice_with_items(db: Session, invoice_id: uuid.UUID) -> Invoice | None:
    invoice = get_invoice_by_id(db, invoice_id)
    if invoice:
        _ = invoice.items  # trigger lazy load
    return invoice


def list_invoices(
    db: Session,
    project_id: uuid.UUID,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Invoice], int, int, int]:
    query = db.query(Invoice).filter(
        Invoice.project_id == project_id,
        Invoice.deleted_at.is_(None),
    )
    if status:
        query = query.filter(Invoice.status == status)
    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Invoice.created_at.desc()).offset(offset).limit(page_size).all()
    return items, total, page, page_size


def update_invoice_status(
    db: Session,
    invoice_id: uuid.UUID,
    status: str,
    paid_at: datetime | None = None,
) -> Invoice | None:
    invoice = get_invoice_by_id(db, invoice_id)
    if not invoice:
        return None
    invoice.status = status
    if paid_at is not None:
        invoice.paid_at = paid_at
    db.commit()
    db.refresh(invoice)
    return invoice


def generate_invoice_number(db: Session) -> str:
    now = datetime.utcnow()
    prefix = f"INV-{now:%Y%m}-"
    last_invoice = db.query(Invoice).filter(
        Invoice.invoice_number.like(f"{prefix}%"),
        Invoice.deleted_at.is_(None),
    ).order_by(Invoice.invoice_number.desc()).first()
    if last_invoice:
        seq = int(last_invoice.invoice_number.split("-")[-1]) + 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"


def soft_delete_invoice(db: Session, invoice_id: uuid.UUID) -> bool:
    invoice = get_invoice_by_id(db, invoice_id)
    if not invoice:
        return False
    invoice.deleted_at = datetime.utcnow()
    db.commit()
    return True
