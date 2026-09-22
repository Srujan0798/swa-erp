import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role, role_includes
from src.backend.db.repositories.project_repo import user_has_project_access
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.sustainability_metric import (
    SustainabilityMetricCreate,
    SustainabilityMetricListResponse,
    SustainabilityMetricRead,
    SustainabilityMetricUpdate,
)
from src.backend.services.sustainability_metric_service import (
    create_metric_service,
    delete_metric_service,
    get_metric_service,
    list_metrics_service,
    update_metric_service,
)

router = APIRouter(
    prefix="/api/projects/{project_id}/sustainability/metrics",
    tags=["sustainability"],
)


def _require_project_access(db: Session, project_id: uuid.UUID, user: User) -> None:
    """Raise 403 when user is not a member of project_id. Admins bypass."""
    if role_includes(Role(user.role), Role.ADMIN):
        return
    if not user_has_project_access(db, user.id, project_id):
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this project's sustainability metrics",
        )


@router.post("", response_model=SustainabilityMetricRead, status_code=status.HTTP_201_CREATED)
def create_metric(
    project_id: uuid.UUID,
    body: SustainabilityMetricCreate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> SustainabilityMetricRead:
    _require_project_access(db, project_id, current_user)
    if body.project_id != project_id:
        raise HTTPException(status_code=422, detail="project_id mismatch")
    result = create_metric_service(db, body.model_dump())
    return SustainabilityMetricRead(**result)


@router.get("", response_model=SustainabilityMetricListResponse)
def list_metrics(
    project_id: uuid.UUID,
    reference_id: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> SustainabilityMetricListResponse:
    _require_project_access(db, project_id, current_user)
    items, total, page, page_size = list_metrics_service(
        db, project_id, reference_id, page=page, page_size=page_size
    )
    return SustainabilityMetricListResponse(
        items=[SustainabilityMetricRead(**r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{metric_id}", response_model=SustainabilityMetricRead)
def get_metric(
    project_id: uuid.UUID,
    metric_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> SustainabilityMetricRead:
    _require_project_access(db, project_id, current_user)
    result = get_metric_service(db, metric_id)
    if not result or result["project_id"] != str(project_id):
        raise HTTPException(status_code=404, detail="Sustainability metric not found")
    return SustainabilityMetricRead(**result)


@router.patch("/{metric_id}", response_model=SustainabilityMetricRead)
def update_metric(
    project_id: uuid.UUID,
    metric_id: uuid.UUID,
    body: SustainabilityMetricUpdate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> SustainabilityMetricRead:
    _require_project_access(db, project_id, current_user)
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = update_metric_service(db, metric_id, data)
    if not result or result["project_id"] != str(project_id):
        raise HTTPException(status_code=404, detail="Sustainability metric not found")
    return SustainabilityMetricRead(**result)


@router.delete("/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_metric(
    project_id: uuid.UUID,
    metric_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    _require_project_access(db, project_id, current_user)
    result = get_metric_service(db, metric_id)
    if not result or result["project_id"] != str(project_id):
        raise HTTPException(status_code=404, detail="Sustainability metric not found")
    delete_metric_service(db, metric_id)
