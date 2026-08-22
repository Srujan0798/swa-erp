import pytest

pytestmark = pytest.mark.asyncio


async def test_create_client(authed_admin_client):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "TestClient",
        "code": "TC-001",
        "primary_email": "tc@example.com",
    })
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "TestClient"
    assert body["code"] == "TC-001"
    assert body["primary_email"] == "tc@example.com"


async def test_duplicate_client_code(authed_admin_client):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "DupClient",
        "code": "DC-001",
        "primary_email": "dc@example.com",
    })
    assert r.status_code == 201

    r2 = await authed_admin_client.post("/api/clients", json={
        "name": "DupClient2",
        "code": "DC-001",
        "primary_email": "dc2@example.com",
    })
    assert r2.status_code == 409


async def test_get_client(authed_admin_client):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "GetClient",
        "code": "GC-001",
        "primary_email": "gc@example.com",
    })
    cid = r.json()["id"]

    r2 = await authed_admin_client.get(f"/api/clients/{cid}")
    assert r2.status_code == 200
    assert r2.json()["name"] == "GetClient"


async def test_update_client(authed_admin_client):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "OldName",
        "code": "UC-001",
        "primary_email": "old@example.com",
    })
    cid = r.json()["id"]

    r2 = await authed_admin_client.patch(f"/api/clients/{cid}", json={
        "name": "NewName",
    })
    assert r2.status_code == 200
    assert r2.json()["name"] == "NewName"
    assert r2.json()["code"] == "UC-001"


async def test_soft_delete_client(authed_admin_client):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "DelClient",
        "code": "DEL-001",
        "primary_email": "del@example.com",
    })
    cid = r.json()["id"]

    r2 = await authed_admin_client.delete(f"/api/clients/{cid}")
    assert r2.status_code == 204

    r3 = await authed_admin_client.get("/api/clients")
    codes = [c["code"] for c in r3.json()["items"]]
    assert "DEL-001" not in codes


async def test_list_clients_pagination(authed_admin_client):
    for i in range(3):
        r = await authed_admin_client.post("/api/clients", json={
            "name": f"PageClient{i}",
            "code": f"PG-{i:03d}",
            "primary_email": f"pg{i}@example.com",
        })
        assert r.status_code == 201

    r = await authed_admin_client.get("/api/clients?page=1&page_size=2")
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 2
    assert body["total"] >= 3


async def test_search_clients(authed_admin_client):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "Searchable Client",
        "code": "SC-001",
        "primary_email": "sc@example.com",
    })
    assert r.status_code == 201

    r2 = await authed_admin_client.get("/api/clients?q=Searchable")
    assert r2.status_code == 200
    assert len(r2.json()["items"]) >= 1


async def test_add_contact(authed_admin_client):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "ContactClient",
        "code": "CC-001",
        "primary_email": "cc@example.com",
    })
    cid = r.json()["id"]

    r2 = await authed_admin_client.post(f"/api/clients/{cid}/contacts", json={
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+91 98765 43210",
        "role": "manager",
    })
    assert r2.status_code == 201
    assert r2.json()["name"] == "John Doe"


async def test_update_contact(authed_admin_client):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "UpdContactClient",
        "code": "UCC-001",
        "primary_email": "ucc@example.com",
    })
    cid = r.json()["id"]

    r2 = await authed_admin_client.post(f"/api/clients/{cid}/contacts", json={
        "name": "Jane",
        "email": "jane@example.com",
    })
    contact_id = r2.json()["id"]

    r3 = await authed_admin_client.patch(f"/api/clients/{cid}/contacts/{contact_id}", json={
        "name": "Jane Updated",
    })
    assert r3.status_code == 200
    assert r3.json()["name"] == "Jane Updated"


async def test_delete_contact(authed_admin_client):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "DelContactClient",
        "code": "DCC-001",
        "primary_email": "dcc@example.com",
    })
    cid = r.json()["id"]

    r2 = await authed_admin_client.post(f"/api/clients/{cid}/contacts", json={
        "name": "Bob",
        "email": "bob@example.com",
    })
    contact_id = r2.json()["id"]

    r3 = await authed_admin_client.delete(f"/api/clients/{cid}/contacts/{contact_id}")
    assert r3.status_code == 204

    r4 = await authed_admin_client.patch(f"/api/clients/{cid}/contacts/{contact_id}", json={
        "name": "Bob Updated",
    })
    assert r4.status_code == 404


async def test_viewer_cannot_create_client(authed_viewer_client):
    r = await authed_viewer_client.post("/api/clients", json={
        "name": "NoAuth",
        "code": "NA-001",
        "primary_email": "na@example.com",
    })
    assert r.status_code == 403


async def test_create_client_excel_sheet_fields(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/clients",
        json={
            "name": "SheetClient",
            "code": "SC-EX-001",
            "primary_email": "sheet@example.com",
            "primary_contact": "Viraj Shah",
            "date_onboarded": "2025-04-01",
            "industry": "HVAC",
            "client_status": "Active",
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["primary_contact"] == "Viraj Shah"
    assert body["date_onboarded"] == "2025-04-01"
    assert body["industry"] == "HVAC"
