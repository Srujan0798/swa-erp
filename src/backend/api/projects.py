import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectRead,
    ProjectUpdate,
)
from src.backend.services.project_service import (
    create_project_service,
    get_project_service,
    list_projects_service,
    soft_delete_project_service,
    update_project_service,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
def list_projects(
    _: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = None,
    status: str | None = None,
) -> ProjectListResponse:
    items, total, page, page_size = list_projects_service(db, page=page, page_size=page_size, q=q, status=status)

    result = []
    for p in items:
        item = ProjectRead.model_validate(p)
        result.append(item)

    return ProjectListResponse(
        items=result,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ProjectRead:
    from sqlalchemy.exc import IntegrityError

    try:
        project = create_project_service(db, body, current_user.id)
        return ProjectRead.model_validate(project)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Project code already exists") from e


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ProjectRead:
    project = get_project_service(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectRead.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: uuid.UUID,
    body: ProjectUpdate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ProjectRead:
    if body.status is not None:
        raise HTTPException(
            status_code=400,
            detail="Use /api/projects/{id}/transition to change status."
        )
    project = update_project_service(db, project_id, body, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectRead.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    success = soft_delete_project_service(db, project_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
