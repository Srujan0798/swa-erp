import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.backend.models.client import Client
from src.backend.models.invoice import Invoice
from src.backend.models.project import Project
from src.backend.models.task import Task
from src.backend.models.time_tracking import TimeEntry
from src.backend.models.user import User
from src.backend.schemas.report import (
    ClientSummaryReport,
    ExecutiveKPIs,
    ProjectHealthReport,
    RevenueForecast,
    UtilizationReport,
)
from src.backend.services.report_service import ReportService


def _seed_user(db, name="Test User", email=None):
    uid = uuid.uuid4()
    u = User(
        id=uid,
        email=email or f"{uid.hex[:8]}@test.com",
        name=name,
        password_hash="x",
        role="pm",
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _seed_client(db, name="Test Client"):
    cid = uuid.uuid4()
    c = Client(
        id=cid,
        name=name,
        code=cid.hex[:8],
        primary_email="c@test.com",
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _seed_project(db, client_id, status="Execution", budget=None, actual=None):
    pid = uuid.uuid4()
    p = Project(
        id=pid,
        client_id=client_id,
        name=f"Project {pid.hex[:6]}",
        code=pid.hex[:8],
        status=status,
        estimated_value=budget,
        actual_value=actual,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _seed_task(db, project_id, user_id, due_date=None, status="todo"):
    tid = uuid.uuid4()
    t = Task(
        id=tid,
        project_id=project_id,
        title=f"Task {tid.hex[:6]}",
        status=status,
        assignee_id=user_id,
        created_by=user_id,
        due_date=due_date,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def _seed_time_entry(db, project_id, user_id, entry_date, hours, billable=True):
    te = TimeEntry(
        project_id=project_id,
        user_id=user_id,
        date=entry_date,
        hours=Decimal(str(hours)),
        description="work",
        is_billable=billable,
    )
    db.add(te)
    db.commit()
    db.refresh(te)
    return te


def _seed_invoice(db, project_id, total, status="paid", created_at=None, created_by=None):
    inv = Invoice(
        project_id=project_id,
        invoice_number=f"INV-{uuid.uuid4().hex[:8]}",
        status=status,
        subtotal=total,
        total=total,
        created_by=created_by or uuid.uuid4(),
    )
    if created_at:
        inv.created_at = created_at
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


@pytest.fixture
def svc():
    return ReportService()


class TestProjectHealth:
    def test_counts_by_status(self, db_session, svc):
        client = _seed_client(db_session)
        _seed_project(db_session, client.id, status="Execution")
        _seed_project(db_session, client.id, status="Execution")
        _seed_project(db_session, client.id, status="Design")

        report = svc.get_project_health(db_session)
        assert isinstance(report, ProjectHealthReport)
        assert report.total_projects == 3
        assert report.by_status["Execution"] == 2
        assert report.by_status["Design"] == 1

    def test_overdue_tasks(self, db_session, svc):
        client = _seed_client(db_session)
        project = _seed_project(db_session, client.id)
        user = _seed_user(db_session)
        _seed_task(db_session, project.id, user.id, due_date=date.today() - timedelta(days=5), status="todo")
        _seed_task(db_session, project.id, user.id, due_date=date.today() + timedelta(days=5), status="todo")

        report = svc.get_project_health(db_session)
        assert report.overdue_tasks == 1

    def test_budget_variance(self, db_session, svc):
        client = _seed_client(db_session)
        _seed_project(db_session, client.id, budget=Decimal("100000"), actual=Decimal("120000"))
        _seed_project(db_session, client.id, budget=Decimal("50000"), actual=Decimal("30000"))

        report = svc.get_project_health(db_session)
        assert report.budget_variance_total == Decimal("0")  # (100k-120k) + (50k-30k)

    def test_empty_database(self, db_session, svc):
        report = svc.get_project_health(db_session)
        assert report.total_projects == 0
        assert report.overdue_tasks == 0
        assert report.budget_variance_total == Decimal("0")
        assert report.at_risk_projects == []


class TestUtilization:
    def test_calculation(self, db_session, svc):
        user = _seed_user(db_session, name="Alice")
        project = _seed_project(db_session, _seed_client(db_session).id)
        today = date.today()
        _seed_time_entry(db_session, project.id, user.id, today, 8, billable=True)
        _seed_time_entry(db_session, project.id, user.id, today, 2, billable=False)

        report = svc.get_utilization(db_session, today, today)
        assert isinstance(report, UtilizationReport)
        assert len(report.members) == 1
        m = report.members[0]
        assert m.billable_hours == Decimal("8")
        assert m.non_billable_hours == Decimal("2")
        assert m.utilization_pct == 80.0

    def test_empty_period(self, db_session, svc):
        report = svc.get_utilization(db_session, date(2020, 1, 1), date(2020, 1, 31))
        assert report.members == []


class TestRevenue:
    def test_monthly_aggregation(self, db_session, svc):
        user = _seed_user(db_session)
        client = _seed_client(db_session)
        project = _seed_project(db_session, client.id)
        _seed_invoice(db_session, project.id, Decimal("10000"), status="paid", created_by=user.id)
        _seed_invoice(db_session, project.id, Decimal("20000"), status="paid", created_by=user.id)
        _seed_invoice(db_session, project.id, Decimal("5000"), status="draft", created_by=user.id)

        report = svc.get_revenue(db_session)
        assert isinstance(report, RevenueForecast)
        paid_total = sum(m.total for m in report.monthly_revenue)
        assert paid_total == Decimal("30000")

    def test_empty_database(self, db_session, svc):
        report = svc.get_revenue(db_session)
        assert report.monthly_revenue == []
        assert report.forecast == []


class TestClientSummary:
    def test_groups_revenue(self, db_session, svc):
        user = _seed_user(db_session)
        c1 = _seed_client(db_session, name="Alpha")
        c2 = _seed_client(db_session, name="Beta")
        p1 = _seed_project(db_session, c1.id)
        p2 = _seed_project(db_session, c2.id)
        _seed_invoice(db_session, p1.id, Decimal("15000"), status="paid", created_by=user.id)
        _seed_invoice(db_session, p2.id, Decimal("25000"), status="paid", created_by=user.id)

        report = svc.get_client_summary(db_session)
        assert isinstance(report, ClientSummaryReport)
        assert len(report.clients) == 2
        alpha = next(c for c in report.clients if c.client_name == "Alpha")
        assert alpha.total_revenue == Decimal("15000")
        assert alpha.project_count == 1

    def test_empty_database(self, db_session, svc):
        report = svc.get_client_summary(db_session)
        assert report.clients == []


class TestExportJson:
    def test_returns_serializable_dict(self, db_session, svc):
        report = svc.get_project_health(db_session)
        result = svc.export_json(report)
        assert isinstance(result, dict)
        assert "total_projects" in result
        assert isinstance(result["by_status"], dict)


class TestExecutiveKPIs:
    def test_empty_database(self, db_session, svc):
        kpis = svc.get_executive_kpis(db_session)
        assert isinstance(kpis, ExecutiveKPIs)
        assert kpis.active_projects == 0
        assert kpis.overdue_tasks == 0
        assert kpis.pipeline_value == Decimal("0")
