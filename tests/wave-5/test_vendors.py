import uuid

import pytest


# ---------------------------------------------------------------------------
# Vendor CRUD
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_vendor(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/vendors",
        json={
            "name": "Test Vendor",
            "code": f"VND-{uuid.uuid4().hex[:6]}",
            "email": "vendor@test.com",
            "phone": "9876543210",
            "address": "123 Street",
            "city": "Mumbai",
            "state": "MH",
            "gst_number": "27AABCU9603R1ZM",
            "pan_number": "AABCU9603R",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Test Vendor"
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_create_vendor_duplicate_code(authed_admin_client):
    code = f"DUP-{uuid.uuid4().hex[:6]}"
    r = await authed_admin_client.post(
        "/api/vendors",
        json={"name": "Vendor A", "code": code},
    )
    assert r.status_code == 201

    r2 = await authed_admin_client.post(
        "/api/vendors",
        json={"name": "Vendor B", "code": code},
    )
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_create_vendor_with_contacts(authed_admin_client):
    code = f"VND-{uuid.uuid4().hex[:6]}"
    r = await authed_admin_client.post(
        "/api/vendors",
        json={
            "name": "Vendor With Contacts",
            "code": code,
            "contacts": [
                {"name": "Primary Contact", "designation": "Manager", "email": "p@test.com", "phone": "1234567890", "is_primary": True},
                {"name": "Secondary Contact", "designation": "Engineer", "email": "s@test.com"},
            ],
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert len(data["contacts"]) == 2
    assert data["contacts"][0]["name"] == "Primary Contact"
    assert data["contacts"][1]["name"] == "Secondary Contact"


@pytest.mark.asyncio
async def test_list_vendors(authed_admin_client):
    code1 = f"VND-{uuid.uuid4().hex[:6]}"
    code2 = f"VND-{uuid.uuid4().hex[:6]}"
    await authed_admin_client.post("/api/vendors", json={"name": "Vendor 1", "code": code1})
    await authed_admin_client.post("/api/vendors", json={"name": "Vendor 2", "code": code2})

    r = await authed_admin_client.get("/api/vendors")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2
    assert data["page"] == 1
    assert data["page_size"] == 20


@pytest.mark.asyncio
async def test_list_vendors_search(authed_admin_client):
    unique = uuid.uuid4().hex[:8]
    code = f"SRCH-{unique}"
    await authed_admin_client.post(
        "/api/vendors",
        json={"name": f"Searchable Vendor {unique}", "code": code},
    )

    r = await authed_admin_client.get(f"/api/vendors?search={unique}")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_vendors_filter_active(authed_admin_client):
    code = f"VND-{uuid.uuid4().hex[:6]}"
    r = await authed_admin_client.post(
        "/api/vendors",
        json={"name": "Active Vendor", "code": code, "is_active": True},
    )
    vendor_id = r.json()["id"]

    r = await authed_admin_client.get("/api/vendors?is_active=true")
    assert r.status_code == 200
    assert r.json()["total"] >= 1

    # Deactivate and verify
    await authed_admin_client.patch(f"/api/vendors/{vendor_id}", json={"is_active": False})
    r = await authed_admin_client.get("/api/vendors?is_active=true")
    ids = [v["id"] for v in r.json()["items"]]
    assert vendor_id not in ids


@pytest.mark.asyncio
async def test_get_vendor(authed_admin_client):
    code = f"VND-{uuid.uuid4().hex[:6]}"
    r = await authed_admin_client.post(
        "/api/vendors",
        json={"name": "Get Vendor", "code": code},
    )
    vendor_id = r.json()["id"]

    r = await authed_admin_client.get(f"/api/vendors/{vendor_id}")
    assert r.status_code == 200
    assert r.json()["code"] == code


@pytest.mark.asyncio
async def test_get_vendor_not_found(authed_admin_client):
    fake_id = str(uuid.uuid4())
    r = await authed_admin_client.get(f"/api/vendors/{fake_id}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_vendor(authed_admin_client):
    code = f"VND-{uuid.uuid4().hex[:6]}"
    r = await authed_admin_client.post(
        "/api/vendors",
        json={"name": "Original Name", "code": code},
    )
    vendor_id = r.json()["id"]

    r = await authed_admin_client.patch(
        f"/api/vendors/{vendor_id}",
        json={"name": "Updated Name", "city": "Delhi"},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Updated Name"
    assert r.json()["city"] == "Delhi"


@pytest.mark.asyncio
async def test_update_vendor_not_found(authed_admin_client):
    fake_id = str(uuid.uuid4())
    r = await authed_admin_client.patch(f"/api/vendors/{fake_id}", json={"name": "X"})
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_vendor(authed_admin_client):
    code = f"VND-{uuid.uuid4().hex[:6]}"
    r = await authed_admin_client.post(
        "/api/vendors",
        json={"name": "To Delete", "code": code},
    )
    vendor_id = r.json()["id"]

    r = await authed_admin_client.delete(f"/api/vendors/{vendor_id}")
    assert r.status_code == 204

    # Should not appear in listing
    r = await authed_admin_client.get("/api/vendors")
    ids = [v["id"] for v in r.json()["items"]]
    assert vendor_id not in ids


@pytest.mark.asyncio
async def test_delete_vendor_not_found(authed_admin_client):
    fake_id = str(uuid.uuid4())
    r = await authed_admin_client.delete(f"/api/vendors/{fake_id}")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Vendor Contacts
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_contact(authed_admin_client):
    code = f"VND-{uuid.uuid4().hex[:6]}"
    r = await authed_admin_client.post(
        "/api/vendors",
        json={"name": "Contact Vendor", "code": code},
    )
    vendor_id = r.json()["id"]

    r = await authed_admin_client.post(
        f"/api/vendors/{vendor_id}/contacts",
        json={"name": "New Contact", "designation": "Director", "email": "dir@test.com", "phone": "9999999999", "is_primary": True},
    )
    assert r.status_code == 201
    assert r.json()["name"] == "New Contact"
    assert r.json()["is_primary"] is True


@pytest.mark.asyncio
async def test_add_contact_vendor_not_found(authed_admin_client):
    fake_id = str(uuid.uuid4())
    r = await authed_admin_client.post(
        f"/api/vendors/{fake_id}/contacts",
        json={"name": "Contact"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_list_contacts(authed_admin_client):
    code = f"VND-{uuid.uuid4().hex[:6]}"
    r = await authed_admin_client.post(
        "/api/vendors",
        json={
            "name": "List Contacts Vendor",
            "code": code,
            "contacts": [
                {"name": "Contact A", "is_primary": True},
                {"name": "Contact B"},
            ],
        },
    )
    vendor_id = r.json()["id"]

    r = await authed_admin_client.get(f"/api/vendors/{vendor_id}/contacts")
    assert r.status_code == 200
    assert len(r.json()) == 2


@pytest.mark.asyncio
async def test_update_contact(authed_admin_client):
    code = f"VND-{uuid.uuid4().hex[:6]}"
    r = await authed_admin_client.post(
        "/api/vendors",
        json={
            "name": "Update Contact Vendor",
            "code": code,
            "contacts": [{"name": "Old Name"}],
        },
    )
    vendor_id = r.json()["id"]
    contact_id = r.json()["contacts"][0]["id"]

    r = await authed_admin_client.patch(
        f"/api/vendors/{vendor_id}/contacts/{contact_id}",
        json={"name": "New Name", "designation": "Lead"},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_contact(authed_admin_client):
    code = f"VND-{uuid.uuid4().hex[:6]}"
    r = await authed_admin_client.post(
        "/api/vendors",
        json={
            "name": "Delete Contact Vendor",
            "code": code,
            "contacts": [{"name": "To Remove"}],
        },
    )
    vendor_id = r.json()["id"]
    contact_id = r.json()["contacts"][0]["id"]

    r = await authed_admin_client.delete(f"/api/vendors/{vendor_id}/contacts/{contact_id}")
    assert r.status_code == 204

    r = await authed_admin_client.get(f"/api/vendors/{vendor_id}/contacts")
    assert r.status_code == 200
    assert len(r.json()) == 0


@pytest.mark.asyncio
async def test_delete_contact_not_found(authed_admin_client):
    code = f"VND-{uuid.uuid4().hex[:6]}"
    r = await authed_admin_client.post(
        "/api/vendors",
        json={"name": "Contact Vendor", "code": code},
    )
    vendor_id = r.json()["id"]
    fake_contact_id = str(uuid.uuid4())

    r = await authed_admin_client.delete(f"/api/vendors/{vendor_id}/contacts/{fake_contact_id}")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Role-based access
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_viewer_cannot_create_vendor(authed_viewer_client):
    r = await authed_viewer_client.post(
        "/api/vendors",
        json={"name": "Viewer Vendor", "code": "V-FAIL"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_viewer_can_list_vendors(authed_viewer_client, authed_admin_client):
    code = f"VND-{uuid.uuid4().hex[:6]}"
    await authed_admin_client.post("/api/vendors", json={"name": "Visible", "code": code})

    r = await authed_viewer_client.get("/api/vendors")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_viewer_cannot_delete_vendor(authed_viewer_client, db_session):
    """Viewer cannot delete vendors - must create vendor via DB to avoid shared client header issue."""
    from src.backend.models.vendor import Vendor
    vendor = Vendor(name="Protected", code=f"VND-{uuid.uuid4().hex[:6]}")
    db_session.add(vendor)
    db_session.commit()
    db_session.refresh(vendor)

    r = await authed_viewer_client.delete(f"/api/vendors/{vendor.id}")
    assert r.status_code == 403
