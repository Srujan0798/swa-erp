import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.backend.core.deps import require_role
from src.backend.core.roles import Role
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


@router.get("/{project_id}/pnl", response_model=ProjectPnLSummary)
def pnl_summary(
    project_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return get_project_pnl(db, project_id)


@router.post("/{project_id}/costs", response_model=ProjectCostRead, status_code=201)
def add_cost(
    project_id: uuid.UUID,
    body: ProjectCostCreate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008  # ADMIN+PM
    db: Session = Depends(get_db),  # noqa: B008
):
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
    return list_project_costs_service(db, project_id, category, page, page_size)


@router.delete("/{project_id}/costs/{cost_id}", status_code=204)
def remove_cost(
    project_id: uuid.UUID,
    cost_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008  # ADMIN+PM; not VIEWER
    db: Session = Depends(get_db),  # noqa: B008
):
    deleted = delete_project_cost(db, cost_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cost entry not found")


@router.get("/{project_id}/costs/breakdown")
def cost_breakdown(
    project_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return get_cost_breakdown(db, project_id)
