import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.backend.models.agreement import ServiceAgreement


def list_agreements(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    client_id: uuid.UUID | None = None,
    inquiry_id: uuid.UUID | None = None,
    status: str | None = None,
    q: str | None = None,
) -> tuple[list[ServiceAgreement], int]:
    query = db.query(ServiceAgreement).filter(ServiceAgreement.deleted_at.is_(None))
    if client_id is not None:
        query = query.filter(ServiceAgreement.client_id == client_id)
    if inquiry_id is not None:
        query = query.filter(ServiceAgreement.inquiry_id == inquiry_id)
    if status:
        query = query.filter(ServiceAgreement.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                ServiceAgreement.reference_id.ilike(like),
                ServiceAgreement.service_name.ilike(like),
            )
        )
    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(ServiceAgreement.created_at.desc()).offset(offset).limit(page_size).all()
    return list(items), total


def get_by_id(db: Session, agreement_id: uuid.UUID) -> ServiceAgreement | None:
    return (
        db.query(ServiceAgreement)
        .filter(ServiceAgreement.id == agreement_id, ServiceAgreement.deleted_at.is_(None))
        .first()
    )


def get_by_reference_id(db: Session, reference_id: str) -> ServiceAgreement | None:
    return (
        db.query(ServiceAgreement)
        .filter(
            ServiceAgreement.reference_id == reference_id, ServiceAgreement.deleted_at.is_(None)
        )
        .first()
    )


def create(db: Session, data: dict[str, Any]) -> ServiceAgreement:
    agreement = ServiceAgreement(**data)
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    return agreement


def update(db: Session, agreement: ServiceAgreement, data: dict[str, Any]) -> ServiceAgreement:
    for k, v in data.items():
        if v is not None:
            setattr(agreement, k, v)
    db.commit()
    db.refresh(agreement)
    return agreement


def soft_delete(db: Session, agreement: ServiceAgreement) -> ServiceAgreement:
    agreement.deleted_at = datetime.now(tz=UTC)
    db.commit()
    db.refresh(agreement)
    return agreement
