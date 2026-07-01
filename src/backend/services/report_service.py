from datetime import date
from decimal import Decimal

from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.backend.db.repositories.report_repo import (
    client_summary_query,
    forecast_query,
    project_health_query,
    revenue_query,
    utilization_query,
)
from src.backend.schemas.report import (
    ClientSummary,
    ClientSummaryReport,
    ExecutiveKPIs,
    ForecastEntry,
    MemberUtilization,
    MonthlyRevenue,
    ProjectHealthReport,
    RevenueForecast,
    UtilizationReport,
)


class ReportService:
    def get_project_health(self, db: Session) -> ProjectHealthReport:
        raw = project_health_query(db)
        return ProjectHealthReport(
            total_projects=raw["total_projects"],
            by_status=raw["by_status"],
            overdue_tasks=raw["overdue_tasks"],
            budget_variance_total=raw["budget_variance_total"],
            at_risk_projects=raw["at_risk_projects"],
        )

    def get_utilization(
        self, db: Session, start_date: date, end_date: date
    ) -> UtilizationReport:
        raw = utilization_query(db, start_date, end_date)
        members = [
            MemberUtilization(
                user_id=m["user_id"],
                name=m["name"],
                billable_hours=m["billable_hours"],
                non_billable_hours=m["non_billable_hours"],
                utilization_pct=m["utilization_pct"],
            )
            for m in raw
        ]
        return UtilizationReport(
            period_start=start_date,
            period_end=end_date,
            members=members,
        )

    def get_revenue(self, db: Session) -> RevenueForecast:
        monthly_raw = revenue_query(db)
        monthly = [
            MonthlyRevenue(month=m["month"], total=m["total"]) for m in monthly_raw
        ]

        forecast_raw = forecast_query(db)
        forecast = [
            ForecastEntry(
                project_id=f["project_id"],
                project_name=f["project_name"],
                pipeline_value=f["pipeline_value"],
                probability=f["probability"],
                expected_value=f["expected_value"],
            )
            for f in forecast_raw
        ]
        return RevenueForecast(monthly_revenue=monthly, forecast=forecast)

    def get_client_summary(self, db: Session) -> ClientSummaryReport:
        raw = client_summary_query(db)
        clients = [
            ClientSummary(
                client_id=c["client_id"],
                client_name=c["client_name"],
                project_count=c["project_count"],
                total_revenue=c["total_revenue"],
            )
            for c in raw
        ]
        return ClientSummaryReport(clients=clients)

    def get_executive_kpis(self, db: Session) -> ExecutiveKPIs:
        health = self.get_project_health(db)
        utilization = self.get_utilization(db, date.today().replace(day=1), date.today())
        revenue = self.get_revenue(db)

        total_revenue_mtd = sum(
            (m.total for m in revenue.monthly_revenue if m.month == date.today().strftime("%Y-%m")),
            Decimal("0"),
        )

        avg_util = 0.0
        if utilization.members:
            avg_util = sum(m.utilization_pct for m in utilization.members) / len(
                utilization.members
            )

        pipeline_value = sum(
            (f.expected_value for f in revenue.forecast), Decimal("0")
        )

        return ExecutiveKPIs(
            active_projects=health.total_projects,
            total_revenue_mtd=total_revenue_mtd,
            avg_utilization=round(avg_util, 2),
            overdue_tasks=health.overdue_tasks,
            pipeline_value=pipeline_value,
        )

    def export_json(self, report: BaseModel) -> dict:
        return report.model_dump(mode="json")


_svc = ReportService()


def get_project_health(db: Session) -> ProjectHealthReport:
    return _svc.get_project_health(db)


def get_utilization(
    db: Session, start_date: date | None = None, end_date: date | None = None
) -> UtilizationReport:
    if start_date is None:
        start_date = date.today().replace(day=1)
    if end_date is None:
        end_date = date.today()
    return _svc.get_utilization(db, start_date, end_date)


def get_revenue(db: Session) -> RevenueForecast:
    return _svc.get_revenue(db)


def get_client_summary(db: Session) -> ClientSummaryReport:
    return _svc.get_client_summary(db)


def get_executive_kpis(db: Session) -> ExecutiveKPIs:
    return _svc.get_executive_kpis(db)
