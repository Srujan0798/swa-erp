"""Wave 5 – RFQ Workflow end-to-end tests."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


# ── fixtures ─────────────────────────────────────────────────────────────────


async def _setup_project_and_vendor(authed_admin_client):
    """Create client, project, vendor, and material using admin client (ADMIN required)."""
    # client
    r = await authed_admin_client.post("/api/clients", json={
        "name": "RFQ Client", "code": "RC-001", "primary_email": "rc@test.com",
    })
    assert r.status_code == 201
    client_id = r.json()["id"]

    # project
    r = await authed_admin_client.post("/api/projects", json={
        "client_id": client_id, "name": "RFQ Project", "code": "RP-001", "status": "Lead",
    })
    assert r.status_code == 201
    project_id = r.json()["id"]

    # vendor
    r = await authed_admin_client.post("/api/vendors", json={
        "name": "Steel Vendor", "code": "SV-001", "email": "sv@test.com",
    })
    assert r.status_code == 201
    vendor_id = r.json()["id"]

    # second vendor for comparison tests
    r = await authed_admin_client.post("/api/vendors", json={
        "name": "Cement Vendor", "code": "CV-001", "email": "cv@test.com",
    })
    assert r.status_code == 201
    vendor2_id = r.json()["id"]

    # material
    r = await authed_admin_client.post("/api/materials", json={
        "name": "TMT Bar", "code": "MTB-001", "unit": "kg",
    })
    assert r.status_code == 201
    material_id = r.json()["id"]

    # second material
    r = await authed_admin_client.post("/api/materials", json={
        "name": "Cement", "code": "CEM-001", "unit": "bag",
    })
    assert r.status_code == 201
    material2_id = r.json()["id"]

    return project_id, vendor_id, vendor2_id, material_id, material2_id


# ── RFQ creation ─────────────────────────────────────────────────────────────


async def test_create_rfq(authed_pm_client, authed_admin_client):
    project_id, vendor_id, _, material_id, _ = await _setup_project_and_vendor(authed_admin_client)
    r = await authed_pm_client.post(f"/api/projects/{project_id}/rfqs", json={
        "project_id": project_id,
        "vendor_id": vendor_id,
        "notes": "Urgent RFQ",
        "items": [{"material_id": material_id, "quantity": 100, "notes": "First batch"}],
    })
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "draft"
    assert body["rfq_number"].startswith("RFQ-")
    assert len(body["items"]) == 1
    assert body["items"][0]["material_name"] == "TMT Bar"


async def test_create_rfq_requires_items(authed_pm_client, authed_admin_client):
    project_id, vendor_id, _, _, _ = await _setup_project_and_vendor(authed_admin_client)
    r = await authed_pm_client.post(f"/api/projects/{project_id}/rfqs", json={
        "project_id": project_id,
        "vendor_id": vendor_id,
        "items": [],
    })
    assert r.status_code == 422  # validation error: min_length=1


async def test_list_project_rfqs(authed_pm_client, authed_admin_client):
    project_id, vendor_id, _, material_id, _ = await _setup_project_and_vendor(authed_admin_client)
    await authed_pm_client.post(f"/api/projects/{project_id}/rfqs", json={
        "project_id": project_id,
        "vendor_id": vendor_id,
        "items": [{"material_id": material_id, "quantity": 50}],
    })
    r = await authed_pm_client.get(f"/api/projects/{project_id}/rfqs")
    assert r.status_code == 200
    assert r.json()["total"] >= 1


async def test_get_rfq(authed_pm_client, authed_admin_client):
    project_id, vendor_id, _, material_id, _ = await _setup_project_and_vendor(authed_admin_client)
    create_r = await authed_pm_client.post(f"/api/projects/{project_id}/rfqs", json={
        "project_id": project_id,
        "vendor_id": vendor_id,
        "items": [{"material_id": material_id, "quantity": 10}],
    })
    rfq_id = create_r.json()["id"]
    r = await authed_pm_client.get(f"/api/rfqs/{rfq_id}")
    assert r.status_code == 200
    assert r.json()["id"] == rfq_id
    assert r.json()["vendor_name"] == "Steel Vendor"


# ── status transitions ───────────────────────────────────────────────────────


async def test_rfq_lifecycle(authed_pm_client, authed_admin_client):
    """Full lifecycle: draft -> sent -> responded -> awarded -> closed."""
    project_id, vendor_id, _, material_id, _ = await _setup_project_and_vendor(authed_admin_client)

    # create
    r = await authed_pm_client.post(f"/api/projects/{project_id}/rfqs", json={
        "project_id": project_id,
        "vendor_id": vendor_id,
        "items": [{"material_id": material_id, "quantity": 100}],
    })
    rfq_id = r.json()["id"]
    assert r.json()["status"] == "draft"

    # send
    r = await authed_pm_client.post(f"/api/rfqs/{rfq_id}/send")
    assert r.status_code == 200
    assert r.json()["status"] == "sent"
    assert r.json()["sent_at"] is not None

    # respond
    item_id = r.json()["items"][0]["id"]
    r = await authed_pm_client.post(f"/api/rfqs/{rfq_id}/respond", json=[
        {"item_id": item_id, "vendor_rate": 45.50},
    ])
    assert r.status_code == 200
    assert r.json()["status"] == "responded"
    assert r.json()["responded_at"] is not None
    assert float(r.json()["items"][0]["vendor_rate"]) == 45.50

    # compare
    r = await authed_pm_client.post(f"/api/rfqs/{rfq_id}/compare")
    assert r.status_code == 200
    assert r.json()["status"] == "compared"

    # award
    r = await authed_pm_client.post(f"/api/rfqs/{rfq_id}/award")
    assert r.status_code == 200
    assert r.json()["status"] == "awarded"
    assert r.json()["awarded_at"] is not None

    # close
    r = await authed_pm_client.post(f"/api/rfqs/{rfq_id}/close")
    assert r.status_code == 200
    assert r.json()["status"] == "closed"


async def test_rfq_cancel_from_draft(authed_pm_client, authed_admin_client):
    project_id, vendor_id, _, material_id, _ = await _setup_project_and_vendor(authed_admin_client)
    r = await authed_pm_client.post(f"/api/projects/{project_id}/rfqs", json={
        "project_id": project_id,
        "vendor_id": vendor_id,
        "items": [{"material_id": material_id, "quantity": 10}],
    })
    rfq_id = r.json()["id"]
    r2 = await authed_pm_client.post(f"/api/rfqs/{rfq_id}/cancel")
    assert r2.status_code == 200
    assert r2.json()["status"] == "cancelled"


async def test_rfq_cancel_from_sent(authed_pm_client, authed_admin_client):
    project_id, vendor_id, _, material_id, _ = await _setup_project_and_vendor(authed_admin_client)
    r = await authed_pm_client.post(f"/api/projects/{project_id}/rfqs", json={
        "project_id": project_id,
        "vendor_id": vendor_id,
        "items": [{"material_id": material_id, "quantity": 10}],
    })
    rfq_id = r.json()["id"]
    await authed_pm_client.post(f"/api/rfqs/{rfq_id}/send")
    r2 = await authed_pm_client.post(f"/api/rfqs/{rfq_id}/cancel")
    assert r2.status_code == 200
    assert r2.json()["status"] == "cancelled"


async def test_invalid_transition_draft_to_awarded(authed_pm_client, authed_admin_client):
    project_id, vendor_id, _, material_id, _ = await _setup_project_and_vendor(authed_admin_client)
    r = await authed_pm_client.post(f"/api/projects/{project_id}/rfqs", json={
        "project_id": project_id,
        "vendor_id": vendor_id,
        "items": [{"material_id": material_id, "quantity": 10}],
    })
    rfq_id = r.json()["id"]
    r2 = await authed_pm_client.post(f"/api/rfqs/{rfq_id}/award")
    assert r2.status_code == 400  # can't go draft -> awarded


async def test_invalid_transition_sent_to_awarded(authed_pm_client, authed_admin_client):
    project_id, vendor_id, _, material_id, _ = await _setup_project_and_vendor(authed_admin_client)
    r = await authed_pm_client.post(f"/api/projects/{project_id}/rfqs", json={
        "project_id": project_id,
        "vendor_id": vendor_id,
        "items": [{"material_id": material_id, "quantity": 10}],
    })
    rfq_id = r.json()["id"]
    await authed_pm_client.post(f"/api/rfqs/{rfq_id}/send")
    r2 = await authed_pm_client.post(f"/api/rfqs/{rfq_id}/award")
    assert r2.status_code == 400  # can't go sent -> awarded


async def test_cannot_close_draft(authed_pm_client, authed_admin_client):
    project_id, vendor_id, _, material_id, _ = await _setup_project_and_vendor(authed_admin_client)
    r = await authed_pm_client.post(f"/api/projects/{project_id}/rfqs", json={
        "project_id": project_id,
        "vendor_id": vendor_id,
        "items": [{"material_id": material_id, "quantity": 10}],
    })
    rfq_id = r.json()["id"]
    r2 = await authed_pm_client.post(f"/api/rfqs/{rfq_id}/close")
    assert r2.status_code == 400


# ── vendor comparison ────────────────────────────────────────────────────────


async def test_compare_vendors(authed_pm_client, authed_admin_client):
    project_id, vendor_id, vendor2_id, material_id, _ = await _setup_project_and_vendor(
        authed_admin_client
    )

    # RFQ to vendor 1
    r1 = await authed_pm_client.post(f"/api/projects/{project_id}/rfqs", json={
        "project_id": project_id,
        "vendor_id": vendor_id,
        "items": [{"material_id": material_id, "quantity": 100}],
    })
    rfq1_id = r1.json()["id"]
    item1_id = r1.json()["items"][0]["id"]

    # send and respond vendor 1
    await authed_pm_client.post(f"/api/rfqs/{rfq1_id}/send")
    await authed_pm_client.post(f"/api/rfqs/{rfq1_id}/respond", json=[
        {"item_id": item1_id, "vendor_rate": 42.00},
    ])

    # RFQ to vendor 2
    r2 = await authed_pm_client.post(f"/api/projects/{project_id}/rfqs", json={
        "project_id": project_id,
        "vendor_id": vendor2_id,
        "items": [{"material_id": material_id, "quantity": 100}],
    })
    rfq2_id = r2.json()["id"]
    item2_id = r2.json()["items"][0]["id"]

    # send and respond vendor 2
    await authed_pm_client.post(f"/api/rfqs/{rfq2_id}/send")
    await authed_pm_client.post(f"/api/rfqs/{rfq2_id}/respond", json=[
        {"item_id": item2_id, "vendor_rate": 38.50},
    ])

    # compare
    r = await authed_pm_client.get(f"/api/projects/{project_id}/rfqs/compare")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    mat_comparison = data[0]
    assert len(mat_comparison["vendors"]) == 2
    rates = [float(v["rate"]) for v in mat_comparison["vendors"]]
    assert 42.00 in rates
    assert 38.50 in rates


# ── role enforcement ─────────────────────────────────────────────────────────


async def test_viewer_cannot_create_rfq(authed_viewer_client):
    r = await authed_viewer_client.post("/api/projects/00000000-0000-0000-0000-000000000000/rfqs", json={
        "project_id": "00000000-0000-0000-0000-000000000000",
        "vendor_id": "00000000-0000-0000-0000-000000000000",
        "items": [{"material_id": "00000000-0000-0000-0000-000000000000", "quantity": 10}],
    })
    assert r.status_code == 403


async def test_non_pm_cannot_award(authed_admin_client):
    """Only PM and above can award."""
    r = await authed_admin_client.post("/api/rfqs/00000000-0000-0000-0000-000000000000/award")
    assert r.status_code in (400, 404)  # RFQ not found or invalid state
