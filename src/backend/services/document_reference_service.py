import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.backend.db.repositories import audit_repo, document_reference_repo
from src.backend.models.document_reference import DocumentReference
from src.backend.schemas.document_reference import (
    DocumentReferenceCreate,
    DocumentReferenceUpdate,
)
from src.backend.services.reference_id_service import generate_reference_id

_SHARED_COUNTER_TYPES = {"DBR", "KDR"}


def _counter_key_for(document_type: str) -> str:
    dt = (document_type or "").strip().upper()
    if dt in _SHARED_COUNTER_TYPES:
        return "DBR"
    return dt[:10] if dt else "DOC"


class ProjectNotFoundError(Exception):
    def __init__(self, project_id: uuid.UUID):
        self.project_id = project_id
        super().__init__(f"Project {project_id} not found")


class TokenNotFoundError(Exception):
    def __init__(self, token_id: uuid.UUID):
        self.token_id = token_id
        super().__init__(f"Token {token_id} not found")


def list_document_references_service(
    db: Session,
    page: int,
    page_size: int,
    project_id: uuid.UUID | None,
    token_id: uuid.UUID | None,
    document_type: str | None,
    q: str | None,
) -> tuple[list[DocumentReference], int, int, int]:
    items, total = document_reference_repo.list_document_references(
        db,
        page=page,
        page_size=page_size,
        project_id=project_id,
        token_id=token_id,
        document_type=document_type,
        q=q,
    )
    return items, total, page, page_size


def get_document_reference_service(db: Session, doc_ref_id: uuid.UUID) -> DocumentReference | None:
    return document_reference_repo.get_by_id(db, doc_ref_id)


def create_document_reference_service(
    db: Session,
    data: DocumentReferenceCreate,
    actor_id: uuid.UUID,
) -> DocumentReference:
    from src.backend.db.repositories.project_repo import get_by_id as get_project_by_id
    from src.backend.db.repositories.token_repo import get_by_id as get_token_by_id

    if not get_project_by_id(db, data.project_id):
        raise ProjectNotFoundError(data.project_id)

    if data.token_id is not None and not get_token_by_id(db, data.token_id):
        raise TokenNotFoundError(data.token_id)

    counter_key = _counter_key_for(data.document_type)
    reference_id = generate_reference_id(db, counter_key)

    payload: dict[str, Any] = {
        "project_id": data.project_id,
        "token_id": data.token_id,
        "doc_date": data.doc_date,
        "document_type": data.document_type,
        "type_": data.type_,
        "author_id": data.author_id,
        "author_name": data.author_name,
        "user_ref": data.user_ref,
        "description": data.description,
        "revision": data.revision or "R0",
        "status": data.status or "Draft",
        "remarks": data.remarks,
        "reference_id": reference_id,
    }

    doc_ref = document_reference_repo.create(db, payload)

    audit_repo.create_entry(
        db,
        action="document_reference.create",
        entity_type="document_reference",
        entity_id=doc_ref.id,
        user_id=actor_id,
        after_json={
            "id": str(doc_ref.id),
            "reference_id": doc_ref.reference_id,
            "project_id": str(doc_ref.project_id),
            "token_id": str(doc_ref.token_id) if doc_ref.token_id else None,
            "document_type": doc_ref.document_type,
            "doc_date": str(doc_ref.doc_date),
            "status": doc_ref.status,
        },
    )
    return doc_ref


def update_document_reference_service(
    db: Session,
    doc_ref_id: uuid.UUID,
    data: DocumentReferenceUpdate,
    actor_id: uuid.UUID,
) -> DocumentReference | None:
    doc_ref = document_reference_repo.get_by_id(db, doc_ref_id)
    if not doc_ref:
        return None
    before = {
        "status": doc_ref.status,
        "revision": doc_ref.revision,
        "description": doc_ref.description,
        "type_": doc_ref.type_,
    }
    update_data = data.model_dump(exclude_unset=True, by_alias=True)
    if "type" in update_data:
        update_data["type_"] = update_data.pop("type")
    document_reference_repo.update(db, doc_ref, update_data)
    audit_repo.create_entry(
        db,
        action="document_reference.update",
        entity_type="document_reference",
        entity_id=doc_ref_id,
        user_id=actor_id,
        before_json=before,
        after_json={
            "status": doc_ref.status,
            "revision": doc_ref.revision,
            "description": doc_ref.description,
            "type_": doc_ref.type_,
        },
    )
    return doc_ref


def soft_delete_document_reference_service(
    db: Session,
    doc_ref_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> bool:
    doc_ref = document_reference_repo.get_by_id(db, doc_ref_id)
    if not doc_ref:
        return False
    document_reference_repo.soft_delete(db, doc_ref)
    audit_repo.create_entry(
        db,
        action="document_reference.delete",
        entity_type="document_reference",
        entity_id=doc_ref_id,
        user_id=actor_id,
        after_json={"deleted_at": str(doc_ref.deleted_at)},
    )
    return True
