import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.sustainability_metric import (
    SustainabilityMetricCreate,
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


@router.post("", response_model=SustainabilityMetricRead, status_code=status.HTTP_201_CREATED)
def create_metric(
    project_id: uuid.UUID,
    body: SustainabilityMetricCreate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> SustainabilityMetricRead:
    if body.project_id != project_id:
        raise HTTPException(status_code=422, detail="project_id mismatch")
    result = create_metric_service(db, body.model_dump())
    return SustainabilityMetricRead(**result)


@router.get("", response_model=list[SustainabilityMetricRead])
def list_metrics(
    project_id: uuid.UUID,
    reference_id: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> list[SustainabilityMetricRead]:
    results = list_metrics_service(db, project_id, reference_id)
    return [SustainabilityMetricRead(**r) for r in results]


@router.get("/{metric_id}", response_model=SustainabilityMetricRead)
def get_metric(
    project_id: uuid.UUID,
    metric_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> SustainabilityMetricRead:
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
    result = get_metric_service(db, metric_id)
    if not result or result["project_id"] != str(project_id):
        raise HTTPException(status_code=404, detail="Sustainability metric not found")
    delete_metric_service(db, metric_id)
