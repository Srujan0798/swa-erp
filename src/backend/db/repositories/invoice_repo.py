import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.backend.models.invoice import Invoice, InvoiceItem
from src.backend.models.time_tracking import TimeEntry

_SEQ_NAME = "invoice_number_seq"


def _next_invoice_number(db: Session) -> str:
    """Atomically obtain the next invoice number from the DB sequence.

    Uses ``nextval('invoice_number_seq')`` inside the current transaction so
    concurrent calls never produce the same suffix.
    """
    now = datetime.now(tz=UTC)
    prefix = f"INV-{now:%Y%m}-"
    db.execute(text(f"CREATE SEQUENCE IF NOT EXISTS {_SEQ_NAME}"))
    row = db.execute(text(f"SELECT nextval('{_SEQ_NAME}') AS n")).fetchone()
    if row is None:
        raise RuntimeError("db sequence nextval returned no row")
    seq = int(row.n)
    return f"{prefix}{seq:04d}"


def create_invoice(
    db: Session,
    data: dict[str, Any],
    items_data: list[dict[str, Any]],
) -> Invoice:
    try:
        entry_ids = [item["time_entry_id"] for item in items_data if item.get("time_entry_id")]
        if len(entry_ids) != len(set(entry_ids)):
            raise ValueError("Time entries cannot appear more than once in an invoice")
        entries = (
            (
                db.query(TimeEntry)
                .filter(TimeEntry.id.in_(entry_ids))
                .order_by(TimeEntry.id)
                .populate_existing()
                .with_for_update()
                .all()
            )
            if entry_ids
            else []
        )
        linked = (
            (
                db.query(InvoiceItem.id)
                .join(Invoice)
                .filter(InvoiceItem.time_entry_id.in_(entry_ids), Invoice.deleted_at.is_(None))
                .first()
            )
            if entry_ids
            else None
        )
        if (
            len(entries) != len(entry_ids)
            or linked
            or any(
                entry.is_billed
                or not entry.is_billable
                or entry.deleted_at is not None
                or entry.project_id != data["project_id"]
                for entry in entries
            )
        ):
            raise ValueError("Time entries are unavailable for billing")
        for entry in entries:
            entry.is_billed = True
        invoice = Invoice(**data)
        db.add(invoice)
        db.flush()
        for item_data in items_data:
            item_data["invoice_id"] = invoice.id
            item = InvoiceItem(**item_data)
            db.add(item)
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(invoice)
    return invoice


def get_invoice_by_id(db: Session, invoice_id: uuid.UUID) -> Invoice | None:
    return (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id,
            Invoice.deleted_at.is_(None),
        )
        .first()
    )


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
    """Public wrapper around ``_next_invoice_number``."""
    return _next_invoice_number(db)


def soft_delete_invoice(db: Session, invoice_id: uuid.UUID) -> bool:
    try:
        invoice = (
            db.query(Invoice)
            .filter(Invoice.id == invoice_id, Invoice.deleted_at.is_(None))
            .populate_existing()
            .with_for_update()
            .first()
        )
        if not invoice:
            return False
        if invoice.status != "draft":
            raise ValueError("Only draft invoices can be deleted")
        entry_ids = [item.time_entry_id for item in invoice.items if item.time_entry_id]
        entries = (
            (
                db.query(TimeEntry)
                .filter(TimeEntry.id.in_(entry_ids))
                .order_by(TimeEntry.id)
                .populate_existing()
                .with_for_update()
                .all()
            )
            if entry_ids
            else []
        )
        linked_ids = (
            {
                row.time_entry_id
                for row in db.query(InvoiceItem.time_entry_id)
                .join(Invoice)
                .filter(
                    InvoiceItem.time_entry_id.in_(entry_ids),
                    Invoice.id != invoice_id,
                    Invoice.deleted_at.is_(None),
                )
                .all()
            }
            if entry_ids
            else set()
        )
        for entry in entries:
            entry.is_billed = entry.id in linked_ids
        invoice.deleted_at = datetime.now(tz=UTC)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True
