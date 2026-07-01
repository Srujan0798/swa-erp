from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class MemberUtilization(BaseModel):
    user_id: str
    name: str
    billable_hours: Decimal
    non_billable_hours: Decimal
    utilization_pct: float


class MonthlyRevenue(BaseModel):
    month: str
    total: Decimal


class ForecastEntry(BaseModel):
    project_id: str
    project_name: str
    pipeline_value: Decimal
    probability: float
    expected_value: Decimal


class ClientSummary(BaseModel):
    client_id: str
    client_name: str
    project_count: int
    total_revenue: Decimal


class ProjectHealthReport(BaseModel):
    total_projects: int
    by_status: dict[str, int]
    overdue_tasks: int
    budget_variance_total: Decimal
    at_risk_projects: list[dict]


class UtilizationReport(BaseModel):
    period_start: date
    period_end: date
    members: list[MemberUtilization]


class RevenueForecast(BaseModel):
    monthly_revenue: list[MonthlyRevenue]
    forecast: list[ForecastEntry]


class ClientSummaryReport(BaseModel):
    clients: list[ClientSummary]


class ExecutiveKPIs(BaseModel):
    active_projects: int
    total_revenue_mtd: Decimal
    avg_utilization: float
    overdue_tasks: int
    pipeline_value: Decimal
