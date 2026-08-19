from datetime import date
from decimal import Decimal

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from src.backend.models.client import Client
from src.backend.models.invoice import Invoice
from src.backend.models.project import Project
from src.backend.models.task import Task
from src.backend.models.time_tracking import TimeEntry
from src.backend.models.user import User

PROBABILITY_MAP = {
    "Lead": 0.1,
    "Quote": 0.3,
    "Awarded": 0.6,
    "Design": 0.7,
    "Vendor": 0.8,
    "Execution": 0.9,
    "Validation": 0.95,
    "Closed": 1.0,
}


def project_health_query(db: Session) -> dict:
    status_rows = (
        db.query(Project.status, func.count(Project.id))
        .filter(Project.deleted_at.is_(None), Project.is_active.is_(True))
        .group_by(Project.status)
        .all()
    )
    by_status = {s: c for s, c in status_rows}
    total_projects = sum(by_status.values())

    overdue_tasks = (
        db.query(func.count(Task.id))
        .filter(
            Task.deleted_at.is_(None),
            Task.due_date < date.today(),
            Task.status != "done",
        )
        .scalar()
        or 0
    )

    budget_variance = db.query(
        func.sum(
            func.coalesce(Project.estimated_value, Decimal("0"))
            - func.coalesce(Project.actual_value, Decimal("0"))
        )
    ).filter(Project.deleted_at.is_(None), Project.is_active.is_(True)).scalar() or Decimal("0")

    at_risk = []
    active_projects = (
        db.query(Project)
        .filter(
            Project.deleted_at.is_(None),
            Project.is_active.is_(True),
            Project.target_end_date < date.today(),
            Project.status.notin_(["Closed", "Validation"]),
        )
        .all()
    )
    for p in active_projects:
        at_risk.append(
            {
                "project_id": str(p.id),
                "name": p.name,
                "status": p.status,
                "target_end_date": str(p.target_end_date),
            }
        )

    return {
        "total_projects": total_projects,
        "by_status": by_status,
        "overdue_tasks": overdue_tasks,
        "budget_variance_total": budget_variance,
        "at_risk_projects": at_risk,
    }


def utilization_query(db: Session, start_date: date, end_date: date) -> list[dict]:
    rows = (
        db.query(
            TimeEntry.user_id,
            User.name,
            func.sum(
                case(
                    (TimeEntry.is_billable.is_(True), TimeEntry.hours),
                    else_=Decimal("0"),
                )
            ).label("billable"),
            func.sum(
                case(
                    (TimeEntry.is_billable.is_(False), TimeEntry.hours),
                    else_=Decimal("0"),
                )
            ).label("non_billable"),
        )
        .join(User, TimeEntry.user_id == User.id)
        .filter(
            TimeEntry.deleted_at.is_(None),
            TimeEntry.date >= start_date,
            TimeEntry.date <= end_date,
        )
        .group_by(TimeEntry.user_id, User.name)
        .all()
    )

    result = []
    for user_id, name, billable, non_billable in rows:
        billable = billable or Decimal("0")
        non_billable = non_billable or Decimal("0")
        total = billable + non_billable
        utilization_pct = float(billable / total * 100) if total > 0 else 0.0
        result.append(
            {
                "user_id": str(user_id),
                "name": name,
                "billable_hours": billable,
                "non_billable_hours": non_billable,
                "utilization_pct": round(utilization_pct, 2),
            }
        )
    return result


def revenue_query(db: Session) -> list[dict]:
    rows = (
        db.query(
            func.to_char(Invoice.created_at, "YYYY-MM").label("month"),
            func.sum(Invoice.total).label("total"),
        )
        .filter(Invoice.deleted_at.is_(None), Invoice.status == "paid")
        .group_by(func.to_char(Invoice.created_at, "YYYY-MM"))
        .order_by(func.to_char(Invoice.created_at, "YYYY-MM"))
        .all()
    )
    return [{"month": m, "total": t or Decimal("0")} for m, t in rows]


def forecast_query(db: Session) -> list[dict]:
    pipeline_statuses = [
        "Lead",
        "Quote",
        "Awarded",
        "Design",
        "Vendor",
        "Execution",
        "Validation",
    ]
    projects = (
        db.query(Project)
        .filter(
            Project.deleted_at.is_(None),
            Project.is_active.is_(True),
            Project.status.in_(pipeline_statuses),
        )
        .all()
    )

    result = []
    for p in projects:
        probability = PROBABILITY_MAP.get(p.status, 0.5)
        pipeline_value = p.estimated_value or Decimal("0")
        expected = pipeline_value * Decimal(str(probability))
        result.append(
            {
                "project_id": str(p.id),
                "project_name": p.name,
                "pipeline_value": pipeline_value,
                "probability": probability,
                "expected_value": expected,
            }
        )
    return result


def client_summary_query(db: Session) -> list[dict]:
    rows = (
        db.query(
            Client.id,
            Client.name,
            func.count(func.distinct(Project.id)).label("project_count"),
            func.coalesce(func.sum(Invoice.total), Decimal("0")).label("total_revenue"),
        )
        .outerjoin(Project, Project.client_id == Client.id)
        .outerjoin(Invoice, Invoice.project_id == Project.id)
        .filter(
            Client.deleted_at.is_(None),
            Client.is_active.is_(True),
        )
        .group_by(Client.id, Client.name)
        .order_by(Client.name)
        .all()
    )
    return [
        {
            "client_id": str(cid),
            "client_name": cname,
            "project_count": pcnt,
            "total_revenue": trev,
        }
        for cid, cname, pcnt, trev in rows
    ]
