import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.backend.models.document_reference import DocumentReference


def list_document_references(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    project_id: uuid.UUID | None = None,
    token_id: uuid.UUID | None = None,
    document_type: str | None = None,
    q: str | None = None,
) -> tuple[list[DocumentReference], int]:
    query = db.query(DocumentReference).filter(DocumentReference.deleted_at.is_(None))
    if project_id is not None:
        query = query.filter(DocumentReference.project_id == project_id)
    if token_id is not None:
        query = query.filter(DocumentReference.token_id == token_id)
    if document_type:
        query = query.filter(DocumentReference.document_type == document_type)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                DocumentReference.reference_id.ilike(like),
                DocumentReference.description.ilike(like),
                DocumentReference.user_ref.ilike(like),
                DocumentReference.remarks.ilike(like),
            )
        )
    total = query.count()
    offset = (page - 1) * page_size
    items = (
        query.order_by(DocumentReference.created_at.desc()).offset(offset).limit(page_size).all()
    )
    return list(items), total


def get_by_id(db: Session, doc_ref_id: uuid.UUID) -> DocumentReference | None:
    return (
        db.query(DocumentReference)
        .filter(
            DocumentReference.id == doc_ref_id,
            DocumentReference.deleted_at.is_(None),
        )
        .first()
    )


def get_by_reference_id(db: Session, reference_id: str) -> DocumentReference | None:
    return (
        db.query(DocumentReference)
        .filter(
            DocumentReference.reference_id == reference_id,
            DocumentReference.deleted_at.is_(None),
        )
        .first()
    )


def create(db: Session, data: dict[str, Any]) -> DocumentReference:
    doc_ref = DocumentReference(**data)
    db.add(doc_ref)
    db.commit()
    db.refresh(doc_ref)
    return doc_ref


def update(db: Session, doc_ref: DocumentReference, data: dict[str, Any]) -> DocumentReference:
    for k, v in data.items():
        if v is not None:
            setattr(doc_ref, k, v)
    db.commit()
    db.refresh(doc_ref)
    return doc_ref


def soft_delete(db: Session, doc_ref: DocumentReference) -> DocumentReference:
    doc_ref.deleted_at = datetime.now(tz=UTC)
    db.commit()
    db.refresh(doc_ref)
    return doc_ref
