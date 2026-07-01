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
        name="Test Project",
        code=f"TP-{uuid.uuid4().hex[:6]}",
        pm_id=admin_user.id,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p.id


def _make_boq_json(items):
    return json.dumps(items).encode("utf-8")


def _boq_item(line, desc="Item", unit="nos", qty=1, rate=100):
    return {
        "line_number": line,
        "description": desc,
        "unit": unit,
        "quantity": qty,
        "rate": rate,
    }


@pytest.mark.asyncio
async def test_list_versions(authed_pm_client, test_project_id):
    items = _make_boq_json([_boq_item(1), _boq_item(2)])
    r = await authed_pm_client.post(
        f"/api/projects/{test_project_id}/boqs",
        files={"file": ("boq1.json", items, "application/json")},
    )
    assert r.status_code == 201

    items2 = _make_boq_json([_boq_item(1, "Item A"), _boq_item(2, "Item B"), _boq_item(3, "Item C")])
    r2 = await authed_pm_client.post(
        f"/api/projects/{test_project_id}/boqs",
        files={"file": ("boq2.json", items2, "application/json")},
    )
    assert r2.status_code == 201

    r = await authed_pm_client.get(f"/api/projects/{test_project_id}/boqs")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_version_detail(authed_pm_client, test_project_id):
    items = _make_boq_json([_boq_item(1, "Concrete"), _boq_item(2, "Steel")])
    r = await authed_pm_client.post(
        f"/api/projects/{test_project_id}/boqs",
        files={"file": ("boq.json", items, "application/json")},
    )
    boq_id = r.json()["id"]

    r = await authed_pm_client.get(f"/api/boqs/{boq_id}")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["description"] == "Concrete"
    assert data["items"][1]["description"] == "Steel"


@pytest.mark.asyncio
async def test_version_items_pagination(authed_pm_client, test_project_id):
    items = _make_boq_json([_boq_item(i, f"Item {i}") for i in range(1, 26)])
    r = await authed_pm_client.post(
        f"/api/projects/{test_project_id}/boqs",
        files={"file": ("boq.json", items, "application/json")},
    )
    boq_id = r.json()["id"]

    r = await authed_pm_client.get(f"/api/boqs/{boq_id}/items?page=1&page_size=10")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 25
    assert len(data["items"]) == 10
    assert data["items"][0]["line_number"] == 1
    assert data["items"][9]["line_number"] == 10

    r = await authed_pm_client.get(f"/api/boqs/{boq_id}/items?page=3&page_size=10")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 5


@pytest.mark.asyncio
async def test_soft_delete_version(authed_pm_client, test_project_id):
    items = _make_boq_json([_boq_item(1)])
    r = await authed_pm_client.post(
        f"/api/projects/{test_project_id}/boqs",
        files={"file": ("boq.json", items, "application/json")},
    )
    boq_id = r.json()["id"]

    r = await authed_pm_client.delete(f"/api/boqs/{boq_id}")
    assert r.status_code == 204

    r = await authed_pm_client.get(f"/api/projects/{test_project_id}/boqs")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_viewer_can_view_but_not_delete(authed_viewer_client, test_project_id):
    items = _make_boq_json([_boq_item(1)])
    r = await authed_viewer_client.post(
        f"/api/projects/{test_project_id}/boqs",
        files={"file": ("boq.json", items, "application/json")},
    )
    assert r.status_code == 403

    r = await authed_viewer_client.get(f"/api/projects/{test_project_id}/boqs")
    assert r.status_code == 200

    boq_items = _make_boq_json([_boq_item(1)])
    r = await authed_viewer_client.post(
        f"/api/projects/{test_project_id}/boqs",
        files={"file": ("boq.json", boq_items, "application/json")},
    )
    assert r.status_code == 403

    r = await authed_viewer_client.get(f"/api/projects/{test_project_id}/boqs")
    assert r.status_code == 200
    if r.json()["total"] > 0:
        boq_id = r.json()["items"][0]["id"]
        r = await authed_viewer_client.delete(f"/api/boqs/{boq_id}")
        assert r.status_code == 403
