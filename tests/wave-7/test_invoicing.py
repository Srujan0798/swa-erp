"""Tests for Invoicing (Task 03)."""
import pytest
from datetime import date, timedelta
from decimal import Decimal

pytestmark = pytest.mark.asyncio


async def _setup_project(authed_admin_client):
    """Helper: create a client and project, return project_id."""
    r = await authed_admin_client.post(
        "/api/clients",
        json={"name": "Inv Client", "code": "INVC-01", "primary_email": "invc@test.com"},
    )
    assert r.status_code == 201
    client_id = r.json()["id"]

    r2 = await authed_admin_client.post(
        "/api/projects",
        json={
            "client_id": str(client_id),
            "name": "Invoice Project",
            "code": "INVP-01",
            "status": "Lead",
        },
    )
    assert r2.status_code == 201
    return r2.json()["id"]


async def test_create_invoice_with_items(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "due_date": (date.today() + timedelta(days=30)).isoformat(),
            "notes": "Test invoice",
            "tax_rate": "18.00",
            "items": [
                {"description": "Design services", "quantity": "10.00", "rate": "5000.00"},
                {"description": "Development", "quantity": "20.00", "rate": "5000.00"},
            ],
        },
    )
    assert r.status_code == 201
    inv = r.json()
    assert inv["status"] == "draft"
    assert inv["currency"] == "INR"
    assert float(inv["subtotal"]) == 150000.00  # (10+20)*5000
    assert float(inv["tax_rate"]) == 18.00
    assert float(inv["tax_amount"]) == 27000.00  # 150000 * 18/100
    assert float(inv["total"]) == 177000.00  # 150000 + 27000


async def test_invoice_number_auto_generate(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Item 1", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    assert r.status_code == 201
    inv_num = r.json()["invoice_number"]
    # Should match INV-YYYYMM-NNNN format
    assert inv_num.startswith("INV-")
    parts = inv_num.split("-")
    assert len(parts) == 3
    assert len(parts[1]) == 6  # YYYYMM
    assert len(parts[2]) == 4  # NNNN


async def test_generate_from_time_entries(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    today = date.today()
    # Create billable time entries
    for i in range(3):
        d = today - timedelta(days=i)
        await authed_admin_client.post(
            "/api/time-entries",
            json={
                "project_id": project_id,
                "date": d.isoformat(),
                "hours": 2.0,
                "description": f"Day {i}",
                "is_billable": True,
            },
        )
    # Generate invoice from time entries
    start = (today - timedelta(days=2)).isoformat()
    end = today.isoformat()
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices/generate-from-time",
        json={"start_date": start, "end_date": end},
    )
    assert r.status_code == 201
    inv = r.json()
    assert len(inv["items"]) == 3
    assert inv["status"] == "draft"
    # Each item should be 2h * 5000 = 10000
    for item in inv["items"]:
        assert float(item["rate"]) == 5000.00


async def test_generate_from_empty_entries(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    today = date.today()
    # Use a date range with no entries
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices/generate-from-time",
        json={
            "start_date": "2020-01-01",
            "end_date": "2020-01-31",
        },
    )
    assert r.status_code == 400


async def test_send_invoice(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Item", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    inv_id = r.json()["id"]
    r2 = await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status",
        json={"status": "sent"},
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "sent"


async def test_mark_invoice_paid(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Item", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    inv_id = r.json()["id"]
    await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status",
        json={"status": "sent"},
    )
    r2 = await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status",
        json={"status": "paid"},
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "paid"
    assert r2.json()["paid_at"] is not None


async def test_cannot_delete_non_draft(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Item", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    inv_id = r.json()["id"]
    await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status",
        json={"status": "sent"},
    )
    r2 = await authed_admin_client.delete(f"/api/invoices/{inv_id}")
    assert r2.status_code == 400


async def test_cannot_mark_paid_again(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Item", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    inv_id = r.json()["id"]
    await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status",
        json={"status": "sent"},
    )
    await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status",
        json={"status": "paid"},
    )
    r2 = await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status",
        json={"status": "paid"},
    )
    assert r2.status_code == 400


async def test_list_invoices_by_project(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    # Create two invoices
    await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "A", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "B", "quantity": "2.00", "rate": "2000.00"},
            ],
        },
    )
    r = await authed_admin_client.get(f"/api/projects/{project_id}/invoices")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 2


async def test_soft_delete_invoice(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "To delete", "quantity": "1.00", "rate": "500.00"},
            ],
        },
    )
    inv_id = r.json()["id"]
    r2 = await authed_admin_client.delete(f"/api/invoices/{inv_id}")
    assert r2.status_code == 204
    # Should not appear in list
    r3 = await authed_admin_client.get(f"/api/projects/{project_id}/invoices")
    ids = [i["id"] for i in r3.json()["items"]]
    assert inv_id not in ids
