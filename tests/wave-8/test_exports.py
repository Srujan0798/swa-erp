import json
import uuid

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture(scope="function")
def test_client_id(db_session):
    from src.backend.models.client import Client

    c = Client(
        name="Test Client",
        code=f"TC-{uuid.uuid4().hex[:6]}",
        primary_email="test@example.com",
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c.id


@pytest.fixture(scope="function")
def test_project_id(db_session, test_client_id, admin_user):
    from src.backend.models.project import Project

    p = Project(
        client_id=test_client_id,
        name="Test Export Project",
        code=f"TE-{uuid.uuid4().hex[:6]}",
        status="Design",
        pm_id=admin_user.id,
        location="Mumbai",
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p.id


def _add_task(db_session, project_id, title, status, created_by):
    from src.backend.models.task import Task

    t = Task(
        project_id=project_id,
        title=title,
        status=status,
        created_by=created_by,
    )
    db_session.add(t)
    db_session.commit()


def _add_boq_with_items(db_session, project_id):
    from src.backend.models.boq import BOQ, BOQItem

    boq = BOQ(
        project_id=project_id,
        version_number=1,
        file_name="demo.json",
        file_path="/tmp/demo.json",
    )
    db_session.add(boq)
    db_session.flush()

    item1 = BOQItem(
        boq_id=boq.id,
        line_number=1,
        category="Civil",
        description="Excavation",
        unit="cum",
        quantity=100,
        rate=500,
        amount=50000,
    )
    item2 = BOQItem(
        boq_id=boq.id,
        line_number=2,
        category="Structural",
        description="Concrete",
        unit="cum",
        quantity=50,
        rate=4000,
        amount=200000,
    )
    db_session.add_all([item1, item2])
    db_session.commit()


@pytest.mark.asyncio
async def test_project_summary_pdf(authed_pm_client, db_session, test_project_id, admin_user):
    _add_task(db_session, test_project_id, "Task 1", "done", admin_user.id)
    _add_task(db_session, test_project_id, "Task 2", "in_progress", admin_user.id)
    _add_task(db_session, test_project_id, "Task 3", "todo", admin_user.id)
    _add_boq_with_items(db_session, test_project_id)

    r = await authed_pm_client.get(f"/api/exports/projects/{test_project_id}/summary.pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_financial_report_pdf(authed_pm_client):
    r = await authed_pm_client.get(
        "/api/exports/reports/financial.pdf",
        params={"start_date": "2026-01-01", "end_date": "2026-06-30"},
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_project_slides_pdf(authed_pm_client, db_session, test_project_id, admin_user):
    _add_task(db_session, test_project_id, "Slide Task", "done", admin_user.id)
    _add_boq_with_items(db_session, test_project_id)

    r = await authed_pm_client.get(f"/api/exports/projects/{test_project_id}/slides.pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_demo_package_json(authed_pm_client, db_session, test_project_id, admin_user):
    _add_task(db_session, test_project_id, "Demo Task", "todo", admin_user.id)
    _add_boq_with_items(db_session, test_project_id)

    r = await authed_pm_client.get(f"/api/exports/projects/{test_project_id}/demo.json")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/json"

    data = r.json()
    assert "project" in data
    assert "boq_items_sample" in data
    assert "tasks" in data
    assert "team" in data
    assert data["project"]["name"] == "Test Export Project"
    assert len(data["boq_items_sample"]) == 2
    assert len(data["tasks"]) == 1


@pytest.mark.asyncio
async def test_unauthorized_401(client, test_project_id):
    r = await client.get(f"/api/exports/projects/{test_project_id}/summary.pdf")
    assert r.status_code in (401, 403)

    r = await client.get(
        "/api/exports/reports/financial.pdf",
        params={"start_date": "2026-01-01", "end_date": "2026-06-30"},
    )
    assert r.status_code in (401, 403)

    r = await client.get(f"/api/exports/projects/{test_project_id}/slides.pdf")
    assert r.status_code in (401, 403)

    r = await client.get(f"/api/exports/projects/{test_project_id}/demo.json")
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_nonexistent_project_404(authed_pm_client):
    fake_id = uuid.uuid4()
    r = await authed_pm_client.get(f"/api/exports/projects/{fake_id}/summary.pdf")
    assert r.status_code == 404

    r = await authed_pm_client.get(f"/api/exports/projects/{fake_id}/slides.pdf")
    assert r.status_code == 404

    r = await authed_pm_client.get(f"/api/exports/projects/{fake_id}/demo.json")
    assert r.status_code == 404
