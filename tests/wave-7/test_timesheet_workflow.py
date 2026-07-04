"""Tests for Timesheet Workflow (Task 02)."""
import pytest
from datetime import date, timedelta

pytestmark = pytest.mark.asyncio


async def _setup_project(authed_admin_client):
    """Helper: create a client and project, return project_id."""
    r = await authed_admin_client.post(
        "/api/clients",
        json={"name": "TSW Client", "code": "TSWC-01", "primary_email": "tswc@test.com"},
    )
    assert r.status_code == 201
    client_id = r.json()["id"]

    r2 = await authed_admin_client.post(
        "/api/projects",
        json={
            "client_id": str(client_id),
            "name": "Timesheet Project",
            "code": "TSP-01",
            "status": "Lead",
        },
    )
    assert r2.status_code == 201
    return r2.json()["id"]


async def test_generate_timesheet_from_entries(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    monday = date.today() - timedelta(days=date.today().weekday())
    # Create 3 entries
    for i in range(3):
        d = monday + timedelta(days=i)
        await authed_admin_client.post(
            "/api/time-entries",
            json={
                "project_id": project_id,
                "date": d.isoformat(),
                "hours": 3.0,
                "description": f"Day {i}",
                "is_billable": True,
            },
        )
    r = await authed_admin_client.post(
        f"/api/timesheets/generate?week_start={monday.isoformat()}",
    )
    assert r.status_code == 200
    ts = r.json()
    assert float(ts["total_hours"]) == 9.0
    assert float(ts["billable_hours"]) == 9.0
    assert ts["status"] == "draft"


async def test_generate_empty_week(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    # Use a future week with no entries
    today = date.today()
    future_monday = today + timedelta(days=(7 - today.weekday()) % 7 or 7)
    r = await authed_admin_client.post(
        f"/api/timesheets/generate?week_start={future_monday.isoformat()}",
    )
    assert r.status_code == 200
    ts = r.json()
    assert float(ts["total_hours"]) == 0.0


async def test_submit_draft_timesheet(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    monday = date.today() - timedelta(days=date.today().weekday())
    await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": monday.isoformat(),
            "hours": 4.0,
            "description": "Work",
        },
    )
    r = await authed_admin_client.post(
        f"/api/timesheets/generate?week_start={monday.isoformat()}",
    )
    ts_id = r.json()["id"]
    r2 = await authed_admin_client.post(f"/api/timesheets/{ts_id}/submit")
    assert r2.status_code == 200
    assert r2.json()["status"] == "submitted"


async def test_submit_non_draft_returns_422(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    monday = date.today() - timedelta(days=date.today().weekday())
    await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": monday.isoformat(),
            "hours": 4.0,
            "description": "Work",
        },
    )
    r = await authed_admin_client.post(
        f"/api/timesheets/generate?week_start={monday.isoformat()}",
    )
    ts_id = r.json()["id"]
    # Submit once
    await authed_admin_client.post(f"/api/timesheets/{ts_id}/submit")
    # Try to submit again (now it's submitted, not draft)
    r2 = await authed_admin_client.post(f"/api/timesheets/{ts_id}/submit")
    assert r2.status_code == 422


async def test_approve_submitted_timesheet(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    monday = date.today() - timedelta(days=date.today().weekday())
    await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": monday.isoformat(),
            "hours": 4.0,
            "description": "Work",
        },
    )
    r = await authed_admin_client.post(
        f"/api/timesheets/generate?week_start={monday.isoformat()}",
    )
    ts_id = r.json()["id"]
    await authed_admin_client.post(f"/api/timesheets/{ts_id}/submit")
    r2 = await authed_admin_client.post(f"/api/timesheets/{ts_id}/approve")
    assert r2.status_code == 200
    body = r2.json()
    assert body["status"] == "approved"
    assert body["approved_by"] is not None
    assert body["approved_at"] is not None


async def test_reject_submitted_timesheet(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    monday = date.today() - timedelta(days=date.today().weekday())
    await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": monday.isoformat(),
            "hours": 4.0,
            "description": "Work",
        },
    )
    r = await authed_admin_client.post(
        f"/api/timesheets/generate?week_start={monday.isoformat()}",
    )
    ts_id = r.json()["id"]
    await authed_admin_client.post(f"/api/timesheets/{ts_id}/submit")
    r2 = await authed_admin_client.post(f"/api/timesheets/{ts_id}/reject")
    assert r2.status_code == 200
    assert r2.json()["status"] == "rejected"


async def test_cannot_create_entry_in_approved_week(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    monday = date.today() - timedelta(days=date.today().weekday())
    # Create entry and approve the week
    r = await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": monday.isoformat(),
            "hours": 4.0,
            "description": "Work",
        },
    )
    r_ts = await authed_admin_client.post(
        f"/api/timesheets/generate?week_start={monday.isoformat()}",
    )
    ts_id = r_ts.json()["id"]
    await authed_admin_client.post(f"/api/timesheets/{ts_id}/submit")
    await authed_admin_client.post(f"/api/timesheets/{ts_id}/approve")
    # Try to add entry in the same week
    r2 = await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": (monday + timedelta(days=1)).isoformat(),
            "hours": 2.0,
            "description": "Should fail",
        },
    )
    assert r2.status_code == 422


async def test_audit_log_on_submit(authed_admin_client, db_session):
    """Verify timesheet submission creates an audit entry."""
    project_id = await _setup_project(authed_admin_client)
    monday = date.today() - timedelta(days=date.today().weekday())
    await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": monday.isoformat(),
            "hours": 4.0,
            "description": "Work",
        },
    )
    r = await authed_admin_client.post(
        f"/api/timesheets/generate?week_start={monday.isoformat()}",
    )
    ts_id = r.json()["id"]
    r2 = await authed_admin_client.post(f"/api/timesheets/{ts_id}/submit")
    assert r2.status_code == 200
    # Check audit log via direct DB query
    from src.backend.models.time_tracking import TimesheetAuditLog

    audit = (
        db_session.query(TimesheetAuditLog)
        .filter(
            TimesheetAuditLog.timesheet_id == ts_id,
            TimesheetAuditLog.action == "submitted",
        )
        .first()
    )
    assert audit is not None


async def test_audit_log_on_approve(authed_admin_client, db_session):
    """Verify timesheet approval creates an audit entry."""
    project_id = await _setup_project(authed_admin_client)
    monday = date.today() - timedelta(days=date.today().weekday())
    await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": monday.isoformat(),
            "hours": 4.0,
            "description": "Work",
        },
    )
    r = await authed_admin_client.post(
        f"/api/timesheets/generate?week_start={monday.isoformat()}",
    )
    ts_id = r.json()["id"]
    await authed_admin_client.post(f"/api/timesheets/{ts_id}/submit")
    await authed_admin_client.post(f"/api/timesheets/{ts_id}/approve")
    from src.backend.models.time_tracking import TimesheetAuditLog

    audit = (
        db_session.query(TimesheetAuditLog)
        .filter(
            TimesheetAuditLog.timesheet_id == ts_id,
            TimesheetAuditLog.action == "approved",
        )
        .first()
    )
    assert audit is not None


async def test_audit_log_on_reject(authed_admin_client, db_session):
    """Verify timesheet rejection creates an audit entry with reason."""
    project_id = await _setup_project(authed_admin_client)
    monday = date.today() - timedelta(days=date.today().weekday())
    await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": monday.isoformat(),
            "hours": 4.0,
            "description": "Work",
        },
    )
    r = await authed_admin_client.post(
        f"/api/timesheets/generate?week_start={monday.isoformat()}",
    )
    ts_id = r.json()["id"]
    await authed_admin_client.post(f"/api/timesheets/{ts_id}/submit")
    await authed_admin_client.post(f"/api/timesheets/{ts_id}/reject")
    from src.backend.models.time_tracking import TimesheetAuditLog

    audit = (
        db_session.query(TimesheetAuditLog)
        .filter(
            TimesheetAuditLog.timesheet_id == ts_id,
            TimesheetAuditLog.action == "rejected",
        )
        .first()
    )
    assert audit is not None
