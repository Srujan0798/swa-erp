import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_create_project(authed_admin_client, db_session):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "ProjectClient", "code": "PC-001", "primary_email": "pc@example.com"
    })
    assert r.status_code == 201
    client_id = r.json()["id"]

    r2 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(client_id),
        "name": "Insulation Audit",
        "code": "PRJ-001",
        "status": "Lead",
    })
    assert r2.status_code == 201
    body = r2.json()
    assert body["code"] == "PRJ-001"
    assert body["status"] == "Lead"
    assert body["client_name"] == "ProjectClient"


async def test_duplicate_project_code(authed_admin_client, db_session):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "DupClient", "code": "DC-001", "primary_email": "dc@example.com"
    })
    assert r.status_code == 201
    cid = r.json()["id"]

    r2 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "A", "code": "DUP-PRJ", "status": "Lead"
    })
    assert r2.status_code == 201

    r3 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "B", "code": "DUP-PRJ", "status": "Lead"
    })
    assert r3.status_code == 409


async def test_filter_by_status(authed_admin_client, db_session):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "FilterClient", "code": "FC-001", "primary_email": "fc@example.com"
    })
    assert r.status_code == 201
    cid = r.json()["id"]

    r2 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "LeadProj", "code": "FL-001", "status": "Lead"
    })
    assert r2.status_code == 201

    r3 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "AwardedProj", "code": "FA-001", "status": "Awarded"
    })
    assert r3.status_code == 201

    r4 = await authed_admin_client.get("/api/projects?status=Lead")
    assert r4.status_code == 200
    assert all(p["status"] == "Lead" for p in r4.json()["items"])


async def test_search_projects(authed_admin_client, db_session):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "SearchClient", "code": "SC-001", "primary_email": "sc@example.com"
    })
    assert r.status_code == 201
    cid = r.json()["id"]

    r2 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "Searchable Project", "code": "FS-001", "status": "Lead"
    })
    assert r2.status_code == 201

    r3 = await authed_admin_client.get("/api/projects?q=Searchable")
    assert r3.status_code == 200
    assert len(r3.json()["items"]) >= 1


async def test_soft_delete_project(authed_admin_client, db_session):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "DelProjClient", "code": "DPC-001", "primary_email": "dpc@example.com"
    })
    assert r.status_code == 201
    cid = r.json()["id"]

    r2 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "DelProj", "code": "FD-001", "status": "Lead"
    })
    assert r2.status_code == 201
    pid = r2.json()["id"]

    r3 = await authed_admin_client.delete(f"/api/projects/{pid}")
    assert r3.status_code == 204

    r4 = await authed_admin_client.get("/api/projects")
    codes = [p["code"] for p in r4.json()["items"]]
    assert "FD-001" not in codes


async def test_assign_pm_to_project(authed_admin_client, admin_user, db_session):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "AssignClient", "code": "AC-001", "primary_email": "ac@example.com"
    })
    assert r.status_code == 201
    cid = r.json()["id"]

    r2 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid),
        "name": "AssignProj",
        "code": "FA-001",
        "status": "Lead",
        "pm_id": str(admin_user.id),
    })
    assert r2.status_code == 201
    assert r2.json()["pm_id"] == str(admin_user.id)