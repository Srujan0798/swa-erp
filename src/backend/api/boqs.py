import os
import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from src.backend.core.boq_parser import BOQParseError
from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.core.storage import get_storage
from src.backend.db.repositories.project_repo import get_by_id as get_project_by_id
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.boq import BOQListResponse, BOQRead
from src.backend.services.boq_service import (
    get_boq_detail,
    get_boq_items_paginated,
    list_boq_versions,
    soft_delete_boq,
    upload_boq,
)

router = APIRouter(tags=["boqs"])


@router.post(
    "/api/projects/{project_id}/boqs",
    response_model=BOQRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_boq_endpoint(
    project_id: uuid.UUID,
    file: UploadFile,
    notes: str | None = Form(default=None),
    current_user: User = Depends(require_role([Role.ADMIN, Role.PM])),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> BOQRead:
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    allowed = {".xlsx", ".json"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed: {ext}. Allowed: {', '.join(sorted(allowed))}",
        )

    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 10MB size limit")

    try:
        return upload_boq(
            db,
            project_id=project_id,
            file_bytes=file_bytes,
            file_name=file.filename or "unknown",
            content_type=file.content_type,
            parsed_by=current_user.id,
            notes=notes,
        )
    except BOQParseError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/api/projects/{project_id}/boqs",
    response_model=BOQListResponse,
)
def list_boqs_endpoint(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> BOQListResponse:
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return list_boq_versions(db, project_id, page=page, page_size=page_size)


@router.get(
    "/api/boqs/{boq_id}",
    response_model=BOQRead,
)
def get_boq_endpoint(
    boq_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> BOQRead:
    result = get_boq_detail(db, boq_id)
    if not result:
        raise HTTPException(status_code=404, detail="BOQ not found")
    return result


@router.get(
    "/api/boqs/{boq_id}/items",
)
def get_boq_items_endpoint(
    boq_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    result = get_boq_items_paginated(db, boq_id, page=page, page_size=page_size)
    return result


@router.get(
    "/api/boqs/{boq_id}/download",
)
def download_boq_endpoint(
    boq_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> Response:
    result = get_boq_detail(db, boq_id)
    if not result:
        raise HTTPException(status_code=404, detail="BOQ not found")
    content = get_storage().read(result.file_path)
    filename = result.file_name or "download"
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete(
    "/api/boqs/{boq_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_boq_endpoint(
    boq_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    success = soft_delete_boq(db, boq_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="BOQ not found")
