import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.backend.core.deps import require_role
from src.backend.core.roles import Role, role_includes
from src.backend.db.repositories.project_repo import user_has_project_access
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.pnl import (
    ProjectCostCreate,
    ProjectCostListResponse,
    ProjectCostRead,
    ProjectPnLSummary,
)
from src.backend.services.project_pnl_service import (
    add_project_cost,
    delete_project_cost,
    get_cost_breakdown,
    get_project_pnl,
    list_project_costs_service,
)

router = APIRouter(prefix="/api/projects", tags=["project-pnl"])


def _require_project_access(db: Session, project_id: uuid.UUID, user: User) -> None:
    """Raise 403 when user is not a member of project_id. Admins bypass."""
    if role_includes(Role(user.role), Role.ADMIN):
        return
    if not user_has_project_access(db, user.id, project_id):
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this project's financials",
        )


@router.get("/{project_id}/pnl", response_model=ProjectPnLSummary)
def pnl_summary(
    project_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    _require_project_access(db, project_id, current_user)
    return get_project_pnl(db, project_id)


@router.post("/{project_id}/costs", response_model=ProjectCostRead, status_code=201)
def add_cost(
    project_id: uuid.UUID,
    body: ProjectCostCreate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008  # ADMIN+PM
    db: Session = Depends(get_db),  # noqa: B008
):
    _require_project_access(db, project_id, current_user)
    return add_project_cost(db, project_id, current_user.id, body)


@router.get("/{project_id}/costs", response_model=ProjectCostListResponse)
def list_costs(
    project_id: uuid.UUID,
    category: str | None = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008  # align with /pnl
    db: Session = Depends(get_db),  # noqa: B008
):
    _require_project_access(db, project_id, current_user)
    return list_project_costs_service(db, project_id, category, page, page_size)


@router.delete("/{project_id}/costs/{cost_id}", status_code=204)
def remove_cost(
    project_id: uuid.UUID,
    cost_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008  # ADMIN+PM; not VIEWER
    db: Session = Depends(get_db),  # noqa: B008
):
    _require_project_access(db, project_id, current_user)
    deleted = delete_project_cost(db, cost_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cost entry not found")


@router.get("/{project_id}/costs/breakdown")
def cost_breakdown(
    project_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    _require_project_access(db, project_id, current_user)
    return get_cost_breakdown(db, project_id)
