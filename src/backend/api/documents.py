import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.repositories.project_repo import get_by_id as get_project_by_id
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.document import (
    DocumentFolderCreate,
    DocumentFolderRead,
    DocumentListResponse,
    DocumentMoveRequest,
    DocumentRead,
    DocumentRenameRequest,
    DocumentUpdate,
    DocumentVersionListResponse,
)
from src.backend.services.document_service import (
    create_folder_service,
    create_new_version,
    delete_folder_service,
    get_document,
    get_version_history,
    list_project_documents,
    list_project_folders,
    move_documents_service,
    rename_document_service,
    rename_folder_service,
    search_project_documents,
    update_document_metadata,
    upload_document,
)

router = APIRouter(tags=["documents"])


def _check_project_exists(db: Session, project_id: uuid.UUID) -> None:
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")


@router.post(
    "/api/projects/{project_id}/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document_endpoint(
    project_id: uuid.UUID,
    file: UploadFile,
    folder_id: uuid.UUID | None = Form(default=None),  # noqa: B008
    tags: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentRead:
    _check_project_exists(db, project_id)

    file_bytes = await file.read()
    if len(file_bytes) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 50MB size limit")

    return upload_document(
        db,
        project_id=project_id,
        file_bytes=file_bytes,
        file_name=file.filename or "unnamed",
        content_type=file.content_type or "application/octet-stream",
        uploaded_by=current_user.id,
        folder_id=folder_id,
        tags=tags,
    )


@router.get(
    "/api/projects/{project_id}/documents",
    response_model=DocumentListResponse,
)
def list_documents_endpoint(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    folder_id: uuid.UUID | None = Query(default=None),  # noqa: B008
) -> DocumentListResponse:
    _check_project_exists(db, project_id)
    result = list_project_documents(db, project_id, page, page_size, folder_id)
    return DocumentListResponse(**result)


@router.get(
    "/api/documents/{document_id}",
    response_model=DocumentRead,
)
def get_document_endpoint(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentRead:
    doc = get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete(
    "/api/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document_endpoint(
    document_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    from src.backend.db.repositories.document_repo import update_document

    doc = get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    update_document(db, document_id, is_active=False)


@router.patch(
    "/api/documents/{document_id}",
    response_model=DocumentRead,
)
def update_document_endpoint(
    document_id: uuid.UUID,
    body: DocumentUpdate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentRead:
    result = update_document_metadata(db, document_id, body, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    return result


@router.post(
    "/api/projects/{project_id}/documents/re-upload",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def reupload_document_endpoint(
    project_id: uuid.UUID,
    original_name: str = Form(...),
    file: UploadFile = Form(...),  # noqa: B008
    tags: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentRead:
    _check_project_exists(db, project_id)

    file_bytes = await file.read()
    if len(file_bytes) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 50MB size limit")

    try:
        return create_new_version(
            db,
            project_id=project_id,
            original_name=original_name,
            file_bytes=file_bytes,
            file_name=file.filename or "unnamed",
            content_type=file.content_type or "application/octet-stream",
            uploaded_by=current_user.id,
            tags=tags,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/api/projects/{project_id}/documents/versions/{name}",
    response_model=DocumentVersionListResponse,
)
def get_version_history_endpoint(
    project_id: uuid.UUID,
    name: str,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentVersionListResponse:
    _check_project_exists(db, project_id)
    return get_version_history(db, project_id, name)


@router.put(
    "/api/documents/{document_id}/rename",
    response_model=DocumentRead,
)
def rename_document_endpoint(
    document_id: uuid.UUID,
    body: DocumentRenameRequest,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentRead:
    result = rename_document_service(db, document_id, body.new_name, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    return result


@router.put(
    "/api/documents/move",
    status_code=status.HTTP_200_OK,
)
def move_documents_endpoint(
    body: DocumentMoveRequest,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> dict:
    try:
        count = move_documents_service(
            db, body.document_ids, body.target_folder_id, current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"moved": count}


@router.post(
    "/api/projects/{project_id}/folders",
    response_model=DocumentFolderRead,
    status_code=status.HTTP_201_CREATED,
)
def create_folder_endpoint(
    project_id: uuid.UUID,
    body: DocumentFolderCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentFolderRead:
    _check_project_exists(db, project_id)
    data = body.model_dump()
    data["project_id"] = project_id
    return create_folder_service(db, DocumentFolderCreate(**data), current_user.id)


@router.get(
    "/api/projects/{project_id}/folders",
    response_model=list[DocumentFolderRead],
)
def list_folders_endpoint(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    parent_id: uuid.UUID | None = Query(default=None),  # noqa: B008
) -> list[DocumentFolderRead]:
    _check_project_exists(db, project_id)
    return list_project_folders(db, project_id, parent_id)


@router.put(
    "/api/folders/{folder_id}/rename",
    response_model=DocumentFolderRead,
)
def rename_folder_endpoint(
    folder_id: uuid.UUID,
    body: DocumentRenameRequest,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentFolderRead:
    result = rename_folder_service(db, folder_id, body.new_name, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Folder not found")
    return result


@router.delete(
    "/api/folders/{folder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_folder_endpoint(
    folder_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    success = delete_folder_service(db, folder_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Folder not found")


@router.get(
    "/api/projects/{project_id}/documents/search",
    response_model=list[DocumentRead],
)
def search_documents_endpoint(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    q: str | None = Query(default=None),
    tags: str | None = Query(default=None),
    folder_id: uuid.UUID | None = Query(default=None),  # noqa: B008
) -> list[DocumentRead]:
    _check_project_exists(db, project_id)
    return search_project_documents(db, project_id, q, tags, folder_id)
