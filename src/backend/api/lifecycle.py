import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.lifecycle import ProjectStatus
from src.backend.core.roles import Role, role_includes
from src.backend.db.repositories.project_repo import user_has_project_access
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.project import ProjectRead
from src.backend.services.lifecycle_service import transition_project

router = APIRouter(prefix="/api/projects", tags=["lifecycle"])


def _require_project_access(db: Session, project_id: uuid.UUID, user: User) -> None:
    """Raise 403 when user is not a member of project_id. Admins bypass."""
    if role_includes(Role(user.role), Role.ADMIN):
        return
    if not user_has_project_access(db, user.id, project_id):
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this project's lifecycle",
        )


class TransitionRequest(BaseModel):
    to_status: ProjectStatus
    reason: str | None = None


class ProjectStatsResponse(BaseModel):
    total_active: int
    by_status: dict[str, int]
    total_estimated_value: Decimal


@router.post("/{project_id}/transition", response_model=ProjectRead)
def transition(
    project_id: uuid.UUID,
    body: TransitionRequest,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    _require_project_access(db, project_id, current_user)
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

    query = (
        db.query(Project.status, func.count(Project.id))
        .filter(Project.deleted_at.is_(None), Project.is_active.is_(True))
        .group_by(Project.status)
    )

    status_counts = {status.value: 0 for status in ProjectStatus}
    for status_val, count in query.all():
        status_counts[status_val] = count

    total_active = sum(status_counts.values())

    total_estimated = (
        db.query(func.sum(Project.estimated_value))
        .filter(Project.deleted_at.is_(None), Project.is_active.is_(True))
        .scalar()
    )

    return ProjectStatsResponse(
        total_active=total_active,
        by_status=status_counts,
        total_estimated_value=(
            Decimal(total_estimated) if total_estimated is not None else Decimal("0")
        ),
    )
