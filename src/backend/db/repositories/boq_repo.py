import uuid
from datetime import UTC, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from src.backend.models.boq import BOQ, BOQItem


def create_boq(
    db: Session,
    *,
    project_id: uuid.UUID,
    version_number: int,
    file_name: str,
    file_path: str,
    parsed_by: uuid.UUID | None = None,
    notes: str | None = None,
    items: list[dict],
) -> BOQ:
    boq = BOQ(
        project_id=project_id,
        version_number=version_number,
        file_name=file_name,
        file_path=file_path,
        parsed_by=parsed_by,
        notes=notes,
    )
    db.add(boq)
    db.flush()

    for item_data in items:
        item = BOQItem(boq_id=boq.id, **item_data)
        db.add(item)

    db.commit()
    db.refresh(boq)
    return boq


def get_next_version_number(db: Session, project_id: uuid.UUID) -> int:
    result = (
        db.query(func.max(BOQ.version_number))
        .filter(
            BOQ.project_id == project_id,
            BOQ.deleted_at.is_(None),
        )
        .scalar()
    )
    return (result or 0) + 1


def get_by_id(db: Session, boq_id: uuid.UUID) -> BOQ | None:
    return (
        db.query(BOQ)
        .options(joinedload(BOQ.items))
        .filter(BOQ.id == boq_id, BOQ.deleted_at.is_(None))
        .first()
    )


def list_by_project(
    db: Session,
    project_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[BOQ], int]:
    query = db.query(BOQ).filter(
        BOQ.project_id == project_id,
        BOQ.deleted_at.is_(None),
    )

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(BOQ.version_number.desc()).offset(offset).limit(page_size).all()

    return items, total


def soft_delete(db: Session, boq_id: uuid.UUID) -> bool:
    boq = db.query(BOQ).filter(BOQ.id == boq_id, BOQ.deleted_at.is_(None)).first()
    if not boq:
        return False
    boq.deleted_at = datetime.now(tz=UTC)
    db.commit()
    return True


def count_items(db: Session, boq_id: uuid.UUID) -> int:
    return db.query(func.count(BOQItem.id)).filter(BOQItem.boq_id == boq_id).scalar() or 0


def list_versions_with_counts(
    db: Session,
    project_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict], int]:
    query = db.query(BOQ).filter(
        BOQ.project_id == project_id,
        BOQ.deleted_at.is_(None),
    )

    total = query.count()
    offset = (page - 1) * page_size
    versions = query.order_by(BOQ.version_number.desc()).offset(offset).limit(page_size).all()

    result = []
    for v in versions:
        item_count = count_items(db, v.id)
        result.append(
            {
                "id": v.id,
                "project_id": v.project_id,
                "version_number": v.version_number,
                "file_name": v.file_name,
                "file_path": v.file_path,
                "parsed_by": v.parsed_by,
                "parsed_at": v.parsed_at,
                "notes": v.notes,
                "is_active": v.is_active,
                "created_at": v.created_at,
                "item_count": item_count,
            }
        )

    return result, total


def list_items_paginated(
    db: Session,
    boq_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[BOQItem], int]:
    query = db.query(BOQItem).filter(BOQItem.boq_id == boq_id)

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(BOQItem.line_number.asc()).offset(offset).limit(page_size).all()

    return items, total
