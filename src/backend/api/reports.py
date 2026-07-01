from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.report import (
    ClientSummaryReport,
    ExecutiveKPIs,
    ProjectHealthReport,
    RevenueForecast,
    UtilizationReport,
)
from src.backend.services.report_service import (
    get_client_summary,
    get_executive_kpis,
    get_project_health,
    get_revenue,
    get_utilization,
)

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/project-health", response_model=ProjectHealthReport)
def project_health(
    _: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ProjectHealthReport:
    return get_project_health(db)


@router.get("/utilization", response_model=UtilizationReport)
def utilization(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    _: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> UtilizationReport:
    return get_utilization(db, start_date=start_date, end_date=end_date)


@router.get("/revenue", response_model=RevenueForecast)
def revenue(
    _: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> RevenueForecast:
    return get_revenue(db)


@router.get("/client-summary", response_model=ClientSummaryReport)
def client_summary(
    _: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ClientSummaryReport:
    return get_client_summary(db)


dashboard_router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@dashboard_router.get("/executive", response_model=ExecutiveKPIs)
def executive(
    _: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ExecutiveKPIs:
    return get_executive_kpis(db)
