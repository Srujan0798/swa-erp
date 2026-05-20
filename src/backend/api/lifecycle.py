import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.lifecycle import ProjectStatus
from src.backend.core.roles import Role
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.project import ProjectRead
from src.backend.services.lifecycle_service import transition_project

router = APIRouter(prefix="/api/projects", tags=["lifecycle"])


class TransitionRequest(BaseModel):
    to_status: ProjectStatus
    reason: str | None = None


class ProjectStatsResponse(BaseModel):
    total_active: int
    by_status: dict[str, int]
    total_estimated_value: float


@router.post("/{project_id}/transition", response_model=ProjectRead)
def transition(
    project_id: uuid.UUID,
    body: TransitionRequest,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    try:
        project = transition_project(db, project_id, body.to_status, current_user.id, body.reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectRead.model_validate(project)


@router.get("/stats", response_model=ProjectStatsResponse)
def project_stats(
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    from src.backend.models.project import Project

    query = db.query(Project.status, func.count(Project.id)).filter(
        Project.deleted_at.is_(None), Project.is_active.is_(True)
    ).group_by(Project.status)

    status_counts = {status.value: 0 for status in ProjectStatus}
    for status_val, count in query.all():
        status_counts[status_val] = count

    total_active = sum(status_counts.values())

    total_estimated = db.query(func.sum(Project.estimated_value)).filter(
        Project.deleted_at.is_(None), Project.is_active.is_(True)
    ).scalar() or 0

    return ProjectStatsResponse(
        total_active=total_active,
        by_status=status_counts,
        total_estimated_value=float(total_estimated),
    )
