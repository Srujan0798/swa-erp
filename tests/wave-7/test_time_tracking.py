"""Tests for Time Tracking (Task 01) and Timesheet Workflow (Task 02)."""
import pytest
from datetime import date, timedelta

from src.backend.db.session import get_db

pytestmark = pytest.mark.asyncio


async def _setup_project(authed_admin_client):
    """Helper: create a client and project, return project_id."""
    r = await authed_admin_client.post(
        "/api/clients",
        json={"name": "TT Client", "code": "TTC-01", "primary_email": "ttc@test.com"},
    )
    assert r.status_code == 201
    client_id = r.json()["id"]

    r2 = await authed_admin_client.post(
        "/api/projects",
        json={
            "client_id": str(client_id),
            "name": "Time Tracking Project",
            "code": "TTP-01",
            "status": "Lead",
        },
    )
    assert r2.status_code == 201
    return r2.json()["id"]


# --- Time Entry CRUD ---


async def test_create_time_entry(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    today = date.today().isoformat()
    r = await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": today,
            "hours": 2.5,
            "description": "Design work",
            "is_billable": True,
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert float(body["hours"]) == 2.5
    assert body["description"] == "Design work"
    assert body["is_billable"] is True
    assert body["project_id"] == project_id


async def test_create_entry_invalid_hours(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    today = date.today().isoformat()
    r = await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": today,
            "hours": 0.33,
            "description": "Bad hours",
        },
    )
    assert r.status_code == 422


async def test_create_entry_hours_exceed_24(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    today = date.today().isoformat()
    r = await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": today,
            "hours": 25,
            "description": "Too many hours",
        },
    )
    assert r.status_code == 422


async def test_list_time_entries_by_project(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    today = date.today().isoformat()
    # Create two entries
    await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": today,
            "hours": 2.0,
            "description": "Entry 1",
        },
    )
    await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": today,
            "hours": 3.0,
            "description": "Entry 2",
        },
    )
    r = await authed_admin_client.get(f"/api/time-entries?project_id={project_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 2


async def test_update_time_entry(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    today = date.today().isoformat()
    r = await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": today,
            "hours": 2.0,
            "description": "Original",
        },
    )
    entry_id = r.json()["id"]
    r2 = await authed_admin_client.patch(
        f"/api/time-entries/{entry_id}",
        json={"description": "Updated", "hours": 3.0},
    )
    assert r2.status_code == 200
    assert r2.json()["description"] == "Updated"
    assert float(r2.json()["hours"]) == 3.0


async def test_delete_time_entry(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    today = date.today().isoformat()
    r = await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": today,
            "hours": 1.5,
            "description": "To delete",
        },
    )
    entry_id = r.json()["id"]
    r2 = await authed_admin_client.delete(f"/api/time-entries/{entry_id}")
    assert r2.status_code == 204
    # Entry should not appear in list
    r3 = await authed_admin_client.get(f"/api/time-entries?project_id={project_id}")
    ids = [e["id"] for e in r3.json()["items"]]
    assert entry_id not in ids


# --- Timesheet Workflow ---


async def test_generate_timesheet(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    today = date.today()
    # Create entries for this week (Mon, Tue, Wed)
    monday = today - timedelta(days=today.weekday())
    for i in range(3):
        d = monday + timedelta(days=i)
        await authed_admin_client.post(
            "/api/time-entries",
            json={
                "project_id": project_id,
                "date": d.isoformat(),
                "hours": 2.0,
                "description": f"Day {i}",
            },
        )
    # Generate timesheet for this week
    monday = today - timedelta(days=today.weekday())
    r = await authed_admin_client.post(
        f"/api/timesheets/generate?week_start={monday.isoformat()}",
    )
    assert r.status_code == 200
    ts = r.json()
    assert float(ts["total_hours"]) == 6.0
    assert ts["status"] == "draft"


async def test_submit_timesheet(authed_admin_client, db_session):
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


async def test_approve_timesheet(authed_admin_client, db_session):
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
    assert r2.json()["status"] == "approved"
    assert r2.json()["approved_by"] is not None


async def test_reject_timesheet(authed_admin_client, db_session):
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


async def test_cannot_edit_entry_in_approved_week(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    monday = date.today() - timedelta(days=date.today().weekday())
    r = await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": monday.isoformat(),
            "hours": 4.0,
            "description": "Work",
        },
    )
    entry_id = r.json()["id"]
    # Generate, submit, approve
    r_ts = await authed_admin_client.post(
        f"/api/timesheets/generate?week_start={monday.isoformat()}",
    )
    ts_id = r_ts.json()["id"]
    await authed_admin_client.post(f"/api/timesheets/{ts_id}/submit")
    await authed_admin_client.post(f"/api/timesheets/{ts_id}/approve")
    # Try to edit entry in approved week
    r2 = await authed_admin_client.patch(
        f"/api/time-entries/{entry_id}",
        json={"description": "Should fail"},
    )
    assert r2.status_code == 422


async def test_non_owner_cannot_update_entry(
    authed_pm_client, authed_admin_client, db_session
):
    from httpx import ASGITransport, AsyncClient
    from src.backend.main import app as _app

    project_id = await _setup_project(authed_admin_client)
    today = date.today().isoformat()
    r = await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": today,
            "hours": 2.0,
            "description": "Admin entry",
        },
    )
    entry_id = r.json()["id"]
    # PM tries to update admin's entry — use a separate client
    async with AsyncClient(transport=ASGITransport(app=_app), base_url="http://test") as pm_client:
        _app.dependency_overrides[get_db] = lambda: db_session
        r_login = await pm_client.post(
            "/api/auth/login",
            json={"email": "pm@swa.co.in", "password": "pm123!"},
        )
        pm_client.headers["Authorization"] = f"Bearer {r_login.json()['access_token']}"
        r2 = await pm_client.patch(
            f"/api/time-entries/{entry_id}",
            json={"description": "Hacked"},
        )
        assert r2.status_code == 403
