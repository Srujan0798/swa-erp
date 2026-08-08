import uuid

from sqlalchemy.orm import Session

from src.backend.core.storage import get_storage
from src.backend.db.repositories.audit_repo import create_entry
from src.backend.db.repositories.document_repo import (
    create_document,
    create_folder,
    delete_folder,
    get_by_id,
    get_folder_by_id,
    get_latest_version,
    get_version_chain,
    list_documents,
    search_documents,
)
from src.backend.db.repositories.document_repo import (
    move_documents as repo_move_documents,
)
from src.backend.db.repositories.document_repo import (
    rename_folder as repo_rename_folder,
)
from src.backend.db.repositories.document_repo import (
    update_document as repo_update_document,
)
from src.backend.schemas.document import (
    DocumentCreate,
    DocumentFolderCreate,
    DocumentFolderRead,
    DocumentRead,
    DocumentUpdate,
    DocumentVersionListResponse,
)


def _record_event(
    db: Session,
    action: str,
    user_id: uuid.UUID | None = None,
    entity_id: uuid.UUID | None = None,
    before_json: dict | None = None,
    after_json: dict | None = None,
) -> None:
    create_entry(
        db,
        action=action,
        entity_type="document",
        user_id=user_id,
        entity_id=entity_id,
        before_json=before_json,
        after_json=after_json,
    )


def _doc_to_dict(doc) -> dict:
    return {
        "id": str(doc.id),
        "project_id": str(doc.project_id),
        "folder_id": str(doc.folder_id) if doc.folder_id else None,
        "name": doc.name,
        "version_number": doc.version_number,
        "tags": doc.tags,
    }


def upload_document(
    db: Session,
    project_id: uuid.UUID,
    file_bytes: bytes,
    file_name: str,
    content_type: str,
    uploaded_by: uuid.UUID | None = None,
    folder_id: uuid.UUID | None = None,
    tags: str | None = None,
) -> DocumentRead:
    stored_name = f"{uuid.uuid4().hex}_{file_name}"
    key = f"{project_id}/{stored_name}"
    file_path = get_storage().save(key, file_bytes)

    data = DocumentCreate(
        project_id=project_id,
        folder_id=folder_id,
        name=file_name,
        stored_name=stored_name,
        file_path=file_path,
        file_size=len(file_bytes),
        content_type=content_type,
        uploaded_by=uploaded_by,
        tags=tags,
    )
    doc = create_document(db, data.model_dump())
    return DocumentRead.model_validate(doc)


def get_document(db: Session, document_id: uuid.UUID) -> DocumentRead | None:
    doc = get_by_id(db, document_id)
    if not doc:
        return None
    return DocumentRead.model_validate(doc)


def list_project_documents(
    db: Session,
    project_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
    folder_id: uuid.UUID | None = None,
) -> dict:
    items, total, page, page_size = list_documents(db, project_id, page, page_size, folder_id)
    return {
        "items": [DocumentRead.model_validate(d) for d in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def search_project_documents(
    db: Session,
    project_id: uuid.UUID,
    q: str | None = None,
    tags: str | None = None,
    folder_id: uuid.UUID | None = None,
) -> list[DocumentRead]:
    docs = search_documents(db, project_id, q, tags, folder_id)
    return [DocumentRead.model_validate(d) for d in docs]


def update_document_metadata(
    db: Session,
    document_id: uuid.UUID,
    update_data: DocumentUpdate,
    actor_id: uuid.UUID | None = None,
) -> DocumentRead | None:
    doc = get_by_id(db, document_id)
    if not doc:
        return None

    before_json = _doc_to_dict(doc)

    update_fields = update_data.model_dump(exclude_unset=True)
    updated = repo_update_document(db, document_id, **update_fields)
    if not updated:
        return None

    after_json = _doc_to_dict(updated)
    _record_event(
        db,
        action="document.update",
        user_id=actor_id,
        entity_id=document_id,
        before_json=before_json,
        after_json=after_json,
    )

    return DocumentRead.model_validate(updated)


def create_new_version(
    db: Session,
    project_id: uuid.UUID,
    original_name: str,
    file_bytes: bytes,
    file_name: str,
    content_type: str,
    uploaded_by: uuid.UUID | None = None,
    tags: str | None = None,
) -> DocumentRead:
    latest = get_latest_version(db, project_id, original_name)
    if not latest:
        raise ValueError(f"Document '{original_name}' not found")

    new_version = latest.version_number + 1
    stored_name = f"{uuid.uuid4().hex}_{file_name}"
    key = f"{project_id}/{stored_name}"
    file_path = get_storage().save(key, file_bytes)

    data = DocumentCreate(
        project_id=project_id,
        folder_id=latest.folder_id,
        name=original_name,
        stored_name=stored_name,
        file_path=file_path,
        file_size=len(file_bytes),
        content_type=content_type,
        uploaded_by=uploaded_by,
        tags=tags or latest.tags,
        version_number=new_version,
        parent_version_id=latest.id,
    )
    doc = create_document(db, data.model_dump())

    _record_event(
        db,
        action="document.version",
        user_id=uploaded_by,
        entity_id=doc.id,
        after_json=_doc_to_dict(doc),
    )

    return DocumentRead.model_validate(doc)


def get_version_history(
    db: Session,
    project_id: uuid.UUID,
    name: str,
) -> DocumentVersionListResponse:
    versions = get_version_chain(db, project_id, name)
    current_version = max((v.version_number for v in versions), default=0)
    return DocumentVersionListResponse(
        versions=[DocumentRead.model_validate(v) for v in versions],
        current_version=current_version,
    )


def move_documents_service(
    db: Session,
    document_ids: list[uuid.UUID],
    target_folder_id: uuid.UUID | None,
    actor_id: uuid.UUID | None = None,
) -> int:
    docs = []
    for did in document_ids:
        doc = get_by_id(db, did)
        if doc:
            docs.append(doc)

    if not docs:
        return 0

    project_ids = {d.project_id for d in docs}
    if len(project_ids) > 1:
        raise ValueError("All documents must belong to the same project")

    count = repo_move_documents(db, document_ids, target_folder_id)

    _record_event(
        db,
        action="document.move",
        user_id=actor_id,
        after_json={"document_ids": [str(d) for d in document_ids], "target_folder_id": str(target_folder_id) if target_folder_id else None},
    )

    return count


def rename_document_service(
    db: Session,
    document_id: uuid.UUID,
    new_name: str,
    actor_id: uuid.UUID | None = None,
) -> DocumentRead | None:
    doc = get_by_id(db, document_id)
    if not doc:
        return None

    before_json = _doc_to_dict(doc)

    updated = repo_update_document(db, document_id, name=new_name)
    if not updated:
        return None

    _record_event(
        db,
        action="document.rename",
        user_id=actor_id,
        entity_id=document_id,
        before_json=before_json,
        after_json=_doc_to_dict(updated),
    )

    return DocumentRead.model_validate(updated)


def rename_folder_service(
    db: Session,
    folder_id: uuid.UUID,
    new_name: str,
    actor_id: uuid.UUID | None = None,
) -> DocumentFolderRead | None:
    folder = get_folder_by_id(db, folder_id)
    if not folder:
        return None

    updated = repo_rename_folder(db, folder_id, new_name)
    if not updated:
        return None

    _record_event(
        db,
        action="folder.rename",
        user_id=actor_id,
        entity_id=folder_id,
        after_json={"name": new_name},
    )

    return DocumentFolderRead.model_validate(updated)


def create_folder_service(
    db: Session,
    data: DocumentFolderCreate,
    actor_id: uuid.UUID | None = None,
) -> DocumentFolderRead:
    folder = create_folder(db, data.model_dump())
    _record_event(
        db,
        action="folder.create",
        user_id=actor_id,
        entity_id=folder.id,
        after_json={"name": folder.name, "project_id": str(folder.project_id)},
    )
    return DocumentFolderRead.model_validate(folder)


def delete_folder_service(
    db: Session,
    folder_id: uuid.UUID,
    actor_id: uuid.UUID | None = None,
) -> bool:
    success = delete_folder(db, folder_id)
    if success:
        _record_event(
            db,
            action="folder.delete",
            user_id=actor_id,
            entity_id=folder_id,
        )
    return success


def get_folder_service(db: Session, folder_id: uuid.UUID) -> DocumentFolderRead | None:
    folder = get_folder_by_id(db, folder_id)
    if not folder:
        return None
    return DocumentFolderRead.model_validate(folder)


def list_project_folders(
    db: Session,
    project_id: uuid.UUID,
    parent_id: uuid.UUID | None = None,
) -> list[DocumentFolderRead]:
    from src.backend.db.repositories.document_repo import list_folders

    folders = list_folders(db, project_id, parent_id)
    return [DocumentFolderRead.model_validate(f) for f in folders]
