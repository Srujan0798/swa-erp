import re
import uuid
import zlib
from datetime import date, timedelta
from decimal import Decimal

import pytest

asyncio = pytest.mark.asyncio


def _pdf_text(pdf_bytes: bytes) -> str:
    """Extract the (decompressed) text content of an FPDF document."""
    raw = pdf_bytes.decode("latin-1")
    streams = re.findall(r"stream\r?\n(.*?)endstream", raw, re.S)
    parts = []
    for s in streams:
        try:
            parts.append(zlib.decompress(s.encode("latin-1")).decode("latin-1"))
        except Exception:
            parts.append(s)
    return "\n".join(parts)


@asyncio
async def _create_client(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/clients",
        json={"name": "Correctness Client", "code": f"CCT-{uuid.uuid4().hex[:6]}", "primary_email": "cc@test.com"},
    )
    assert r.status_code == 201
    return r.json()["id"]


# ---------------------------------------------------------------------------
# Fix 1 — financial report PDF must use real ProjectCost / time costs
# ---------------------------------------------------------------------------


@asyncio
async def test_financial_report_uses_real_costs_not_ratio(db_session, test_project, admin_user):
    from src.backend.models.boq import BOQ
    from src.backend.models.project_cost import ProjectCost
    from src.backend.models.quote import Quote
    from src.backend.models.time_tracking import TimeEntry
    from src.backend.services.export_service import export_financial_report

    today = date.today()
    boq = BOQ(
        project_id=test_project.id,
        version_number=1,
        file_name="financial.json",
        file_path="/tmp/financial.json",
    )
    db_session.add(boq)
    db_session.flush()

    quote = Quote(
        project_id=test_project.id,
        boq_id=boq.id,
        version_number=1,
        subtotal=Decimal("100000.00"),
        total_amount=Decimal("100000.00"),
        status="sent",
        client_response="accepted",
    )
    db_session.add(quote)
    db_session.flush()

    cost = ProjectCost(
        project_id=test_project.id,
        category="material",
        description="Steel",
        amount=Decimal("15000.00"),
        date=today,
        created_by=admin_user.id,
    )
    db_session.add(cost)
    db_session.flush()

    entry = TimeEntry(
        project_id=test_project.id,
        user_id=admin_user.id,
        date=today,
        hours=Decimal("2.00"),
        description="Engineering",
        is_billable=True,
    )
    db_session.add(entry)
    db_session.commit()

    pdf = export_financial_report(
        db_session, today - timedelta(days=1), today + timedelta(days=1)
    )
    text = _pdf_text(pdf)

    # Real total cost = 15000 (ProjectCost) + 2h * 5000 (billable time) = 25000
    assert "25,000.00" in text, "PDF must show the real aggregated cost"
    # Net P&L = revenue (100000) - costs (25000) = 75000
    assert "75,000.00" in text, "PDF must show real net P&L"
    # The old fabricated 70%/30% ratios of revenue must be gone
    assert "70,000.00" not in text, "fabricated 0.7 * revenue cost must not appear"
    assert "30,000.00" not in text, "fabricated 0.3 * revenue net P&L must not appear"


@asyncio
async def test_financial_report_zero_costs_when_none(db_session, test_project, admin_user):
    from src.backend.models.boq import BOQ
    from src.backend.models.quote import Quote
    from src.backend.services.export_service import export_financial_report

    today = date.today()
    boq = BOQ(
        project_id=test_project.id,
        version_number=1,
        file_name="financial2.json",
        file_path="/tmp/financial2.json",
    )
    db_session.add(boq)
    db_session.flush()
    quote = Quote(
        project_id=test_project.id,
        boq_id=boq.id,
        version_number=1,
        subtotal=Decimal("50000.00"),
        total_amount=Decimal("50000.00"),
        status="sent",
        client_response="accepted",
    )
    db_session.add(quote)
    db_session.commit()

    pdf = export_financial_report(
        db_session, today - timedelta(days=1), today + timedelta(days=1)
    )
    text = _pdf_text(pdf)

    assert "0.00" in text
    assert "50,000.00" in text  # net P&L equals revenue when no costs exist


# ---------------------------------------------------------------------------
# Fix 2 — ProjectStatsResponse.total_estimated_value must be Decimal
# ---------------------------------------------------------------------------


@asyncio
async def test_project_stats_total_estimated_value_is_decimal(
    authed_admin_client, db_session, test_project
):
    from src.backend.models.project import Project

    project = db_session.get(Project, test_project.id)
    project.estimated_value = Decimal("123456.78")
    db_session.commit()

    r = await authed_admin_client.get("/api/projects/stats")
    assert r.status_code == 200
    value = r.json()["total_estimated_value"]
    assert isinstance(value, str), "Decimal must serialize as string, not float"
    assert Decimal(value) == Decimal("123456.78")


# ---------------------------------------------------------------------------
# Fix 3 — task soft delete sets deleted_at; row survives; hidden from queries
# ---------------------------------------------------------------------------


def test_task_soft_delete_sets_deleted_at_and_keeps_row(db_session, test_project, admin_user):
    from sqlalchemy import text

    from src.backend.db.repositories.task_repo import get_by_id, list_by_project, soft_delete
    from src.backend.models.task import Task

    task = Task(
        project_id=test_project.id,
        title="Soft delete me",
        status="todo",
        reporter_id=admin_user.id,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    task_id = task.id

    ok = soft_delete(db_session, task_id)
    db_session.commit()

    assert ok is True

    deleted_at = db_session.execute(
        text("SELECT deleted_at FROM tasks WHERE id = :id"), {"id": str(task_id)}
    ).scalar()
    assert deleted_at is not None, "row must still exist with deleted_at set"

    assert get_by_id(db_session, task_id) is None, "soft-deleted task must not appear in get"
    items, total = list_by_project(db_session, test_project.id, 1, 50, None, None, None)
    assert all(i.id != task_id for i in items), "soft-deleted task must not appear in list"
    assert total == 0


# ---------------------------------------------------------------------------
# Fix 4 — Project optimistic locking via version column
# ---------------------------------------------------------------------------


@asyncio
async def test_project_optimistic_locking_rejects_stale_update(authed_admin_client, db_session):
    client_id = await _create_client(authed_admin_client)
    r = await authed_admin_client.post(
        "/api/projects",
        json={
            "client_id": str(client_id),
            "name": "OL Project",
            "code": f"OL-{uuid.uuid4().hex[:6]}",
            "status": "Lead",
        },
    )
    assert r.status_code == 201
    project_id = r.json()["id"]
    assert r.json()["version"] == 1

    r2 = await authed_admin_client.patch(
        f"/api/projects/{project_id}",
        json={"name": "Updated", "expected_version": 1},
    )
    assert r2.status_code == 200
    assert r2.json()["version"] == 2

    r3 = await authed_admin_client.patch(
        f"/api/projects/{project_id}",
        json={"name": "Stale", "expected_version": 1},
    )
    assert r3.status_code == 409
    assert "modified" in r3.json()["detail"].lower()


@asyncio
async def test_project_update_without_expected_version_still_succeeds(
    authed_admin_client, db_session
):
    client_id = await _create_client(authed_admin_client)
    r = await authed_admin_client.post(
        "/api/projects",
        json={
            "client_id": str(client_id),
            "name": "No Version Project",
            "code": f"NV-{uuid.uuid4().hex[:6]}",
            "status": "Lead",
        },
    )
    assert r.status_code == 201
    project_id = r.json()["id"]
    assert r.json()["version"] == 1

    r2 = await authed_admin_client.patch(
        f"/api/projects/{project_id}", json={"description": "no version sent"}
    )
    assert r2.status_code == 200
    assert r2.json()["version"] == 2
