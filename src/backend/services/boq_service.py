import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from src.backend.core.boq_parser import parse_excel, parse_json
from src.backend.core.storage import get_storage
from src.backend.db.repositories.audit_repo import create_entry
from src.backend.db.repositories.boq_repo import (
    create_boq,
    get_by_id,
    get_next_version_number,
    list_by_project,
    list_items_paginated,
    list_versions_with_counts,
    soft_delete,
)
from src.backend.models.boq import BOQ
from src.backend.schemas.boq import (
    BOQItemListResponse,
    BOQItemRead,
    BOQListRead,
    BOQListResponse,
    BOQRead,
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".xlsx", ".json"}


def upload_boq(
    db: Session,
    project_id: uuid.UUID,
    file_bytes: bytes,
    file_name: str,
    content_type: str | None,
    parsed_by: uuid.UUID,
    notes: str | None = None,
) -> BOQRead:
    ext = Path(file_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        msg = f"File type not allowed: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        raise ValueError(msg)

    if len(file_bytes) > MAX_FILE_SIZE:
        msg = "File exceeds 10MB size limit"
        raise ValueError(msg)

    if ext == ".xlsx":
        items = parse_excel(file_bytes)
    else:
        items = parse_json(file_bytes)

    version_number = get_next_version_number(db, project_id)

    unique_name = f"{uuid.uuid4()}_{file_name}"
    key = f"boqs/{project_id}/{unique_name}"
    file_path = get_storage().save(key, file_bytes)

    boq = create_boq(
        db,
        project_id=project_id,
        version_number=version_number,
        file_name=file_name,
        file_path=str(file_path),
        parsed_by=parsed_by,
        notes=notes,
        items=items,
    )

    create_entry(
        db,
        action="boq.upload",
        entity_type="boq",
        user_id=parsed_by,
        entity_id=boq.id,
        after_json={
            "project_id": str(project_id),
            "version_number": version_number,
            "file_name": file_name,
            "item_count": len(items),
        },
    )

    return _to_read(boq)


def get_boq(db: Session, boq_id: uuid.UUID) -> BOQRead | None:
    boq = get_by_id(db, boq_id)
    if not boq:
        return None
    return _to_read(boq)


def list_boqs(
    db: Session,
    project_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
) -> BOQListResponse:
    items, total = list_by_project(db, project_id, page=page, page_size=page_size)
    reads = [BOQListRead.model_validate(_to_read(b).model_dump()) for b in items]
    return BOQListResponse(items=reads, total=total, page=page, page_size=page_size)


def delete_boq(db: Session, boq_id: uuid.UUID, actor_id: uuid.UUID) -> bool:
    success = soft_delete(db, boq_id)
    if success:
        create_entry(
            db,
            action="boq.delete",
            entity_type="boq",
            user_id=actor_id,
            entity_id=boq_id,
        )
    return success


def _to_read(boq: BOQ) -> BOQRead:
    return BOQRead(
        id=boq.id,
        project_id=boq.project_id,
        version_number=boq.version_number,
        file_name=boq.file_name,
        parsed_at=boq.parsed_at,
        parsed_by=boq.parsed_by,
        notes=boq.notes,
        is_active=boq.is_active,
        created_at=boq.created_at,
        file_path=boq.file_path,
        items=[BOQItemRead.model_validate(i) for i in boq.items] if boq.items else [],
    )


def list_boq_versions(
    db: Session,
    project_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
) -> BOQListResponse:
    items, total = list_versions_with_counts(db, project_id, page=page, page_size=page_size)
    reads = [BOQListRead(**i) for i in items]
    return BOQListResponse(items=reads, total=total, page=page, page_size=page_size)


def get_boq_detail(db: Session, boq_id: uuid.UUID) -> BOQRead | None:
    boq = get_by_id(db, boq_id)
    if not boq:
        return None
    return BOQRead(
        id=boq.id,
        project_id=boq.project_id,
        version_number=boq.version_number,
        file_name=boq.file_name,
        parsed_at=boq.parsed_at,
        parsed_by=boq.parsed_by,
        notes=boq.notes,
        is_active=boq.is_active,
        created_at=boq.created_at,
        file_path=boq.file_path,
        items=[BOQItemRead.model_validate(i) for i in boq.items] if boq.items else [],
    )


def get_boq_items_paginated(
    db: Session,
    boq_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
) -> BOQItemListResponse:
    items, total = list_items_paginated(db, boq_id, page=page, page_size=page_size)
    reads = [BOQItemRead.model_validate(i) for i in items]
    return BOQItemListResponse(items=reads, total=total, page=page, page_size=page_size)


def soft_delete_boq(
    db: Session,
    boq_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> bool:
    boq = get_by_id(db, boq_id)
    if not boq:
        return False

    before_json = {
        "id": str(boq.id),
        "project_id": str(boq.project_id),
        "version_number": boq.version_number,
        "file_name": boq.file_name,
    }

    success = soft_delete(db, boq_id)

    if success:
        create_entry(
            db,
            action="boq.delete",
            entity_type="boq",
            user_id=actor_id,
            entity_id=boq_id,
            before_json=before_json,
        )

    return success
