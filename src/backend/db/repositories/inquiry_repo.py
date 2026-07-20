import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.backend.models.inquiry import Inquiry


def list_inquiries(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    q: str | None = None,
    status: str | None = None,
) -> tuple[list[Inquiry], int]:
    query = db.query(Inquiry).filter(Inquiry.deleted_at.is_(None))
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Inquiry.client_name.ilike(like),
                Inquiry.reference_id.ilike(like),
                Inquiry.requirement_summary.ilike(like),
            )
        )
    if status:
        query = query.filter(Inquiry.status == status)
    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Inquiry.created_at.desc()).offset(offset).limit(page_size).all()
    return list(items), total


def get_by_id(db: Session, inquiry_id: uuid.UUID) -> Inquiry | None:
    return (
        db.query(Inquiry)
        .filter(Inquiry.id == inquiry_id, Inquiry.deleted_at.is_(None))
        .first()
    )


def get_by_reference_id(db: Session, reference_id: str) -> Inquiry | None:
    return (
        db.query(Inquiry)
        .filter(Inquiry.reference_id == reference_id, Inquiry.deleted_at.is_(None))
        .first()
    )


def create(db: Session, data: dict[str, Any]) -> Inquiry:
    inquiry = Inquiry(**data)
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    return inquiry


def update(db: Session, inquiry: Inquiry, data: dict[str, Any]) -> Inquiry:
    for k, v in data.items():
        if v is not None:
            setattr(inquiry, k, v)
    db.commit()
    db.refresh(inquiry)
    return inquiry


def soft_delete(db: Session, inquiry: Inquiry) -> Inquiry:
    inquiry.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(inquiry)
    return inquiry
