"""Tests for Project P&L (Task 04)."""
import pytest
from datetime import date, timedelta
from decimal import Decimal

pytestmark = pytest.mark.asyncio


async def _setup_project(authed_admin_client):
    """Helper: create a client and project, return project_id."""
    r = await authed_admin_client.post(
        "/api/clients",
        json={"name": "PnL Client", "code": "PNLC-01", "primary_email": "pnlc@test.com"},
    )
    assert r.status_code == 201
    client_id = r.json()["id"]

    r2 = await authed_admin_client.post(
        "/api/projects",
        json={
            "client_id": str(client_id),
            "name": "PnL Project",
            "code": "PNLP-01",
            "status": "Lead",
        },
    )
    assert r2.status_code == 201
    return r2.json()["id"]


async def test_pnl_empty_project(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.get(f"/api/projects/{project_id}/pnl")
    assert r.status_code == 200
    pnl = r.json()
    assert float(pnl["total_revenue"]) == 0.0
    assert float(pnl["total_costs"]) == 0.0
    assert float(pnl["net_profit"]) == 0.0
    assert float(pnl["margin_pct"]) == 0.0


async def test_pnl_with_time_costs(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    today = date.today()
    # Create billable time entries
    for i in range(2):
        await authed_admin_client.post(
            "/api/time-entries",
            json={
                "project_id": project_id,
                "date": (today - timedelta(days=i)).isoformat(),
                "hours": 4.0,
                "description": f"Day {i}",
                "is_billable": True,
            },
        )
    r = await authed_admin_client.get(f"/api/projects/{project_id}/pnl")
    assert r.status_code == 200
    pnl = r.json()
    # 8 hours * 5000 INR/hr = 40000
    assert float(pnl["total_costs"]) == 40000.0
    # Check time category in breakdown
    time_items = [b for b in pnl["cost_breakdown"] if b["category"] == "time"]
    assert len(time_items) == 1
    assert float(time_items[0]["amount"]) == 40000.0


async def test_pnl_with_manual_costs(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    # Add manual costs
    await authed_admin_client.post(
        f"/api/projects/{project_id}/costs",
        json={
            "project_id": str(project_id),
            "category": "material",
            "description": "Steel beams",
            "amount": "50000.00",
            "date": date.today().isoformat(),
        },
    )
    await authed_admin_client.post(
        f"/api/projects/{project_id}/costs",
        json={
            "project_id": str(project_id),
            "category": "vendor",
            "description": "Contractor fee",
            "amount": "30000.00",
            "date": date.today().isoformat(),
        },
    )
    r = await authed_admin_client.get(f"/api/projects/{project_id}/pnl")
    assert r.status_code == 200
    pnl = r.json()
    assert float(pnl["total_costs"]) == 80000.0
    cats = {b["category"]: float(b["amount"]) for b in pnl["cost_breakdown"]}
    assert cats["material"] == 50000.0
    assert cats["vendor"] == 30000.0


async def test_pnl_revenue_from_invoices(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    # Create invoice and mark as paid
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Service", "quantity": "1.00", "rate": "100000.00"},
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
    r2 = await authed_admin_client.get(f"/api/projects/{project_id}/pnl")
    assert r2.status_code == 200
    pnl = r2.json()
    assert float(pnl["total_revenue"]) == 118000.0  # 100000 subtotal + 18% GST


async def test_pnl_excludes_unpaid_invoices(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    # Create draft invoice (not paid)
    await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Draft", "quantity": "1.00", "rate": "50000.00"},
            ],
        },
    )
    r = await authed_admin_client.get(f"/api/projects/{project_id}/pnl")
    assert r.status_code == 200
    assert float(r.json()["total_revenue"]) == 0.0


async def test_cost_breakdown_by_category(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    await authed_admin_client.post(
        f"/api/projects/{project_id}/costs",
        json={
            "project_id": str(project_id),
            "category": "material",
            "description": "Item A",
            "amount": "10000.00",
            "date": date.today().isoformat(),
        },
    )
    await authed_admin_client.post(
        f"/api/projects/{project_id}/costs",
        json={
            "project_id": str(project_id),
            "category": "overhead",
            "description": "Rent",
            "amount": "5000.00",
            "date": date.today().isoformat(),
        },
    )
    r = await authed_admin_client.get(f"/api/projects/{project_id}/costs/breakdown")
    assert r.status_code == 200
    breakdown = r.json()
    cats = {b["category"]: float(b["amount"]) for b in breakdown}
    assert cats["material"] == 10000.0
    assert cats["overhead"] == 5000.0


async def test_add_manual_cost(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/costs",
        json={
            "project_id": str(project_id),
            "category": "other",
            "description": "Miscellaneous",
            "amount": "1500.00",
            "date": date.today().isoformat(),
        },
    )
    assert r.status_code == 201
    cost = r.json()
    assert float(cost["amount"]) == 1500.0
    assert cost["category"] == "other"
    # Verify it appears in P&L
    r2 = await authed_admin_client.get(f"/api/projects/{project_id}/pnl")
    assert r2.status_code == 200
    cats = {b["category"]: float(b["amount"]) for b in r2.json()["cost_breakdown"]}
    assert cats["other"] == 1500.0


async def test_delete_cost(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/costs",
        json={
            "project_id": str(project_id),
            "category": "material",
            "description": "To delete",
            "amount": "2000.00",
            "date": date.today().isoformat(),
        },
    )
    cost_id = r.json()["id"]
    r2 = await authed_admin_client.delete(f"/api/projects/{project_id}/costs/{cost_id}")
    assert r2.status_code == 204
    # P&L should have 0 material costs
    r3 = await authed_admin_client.get(f"/api/projects/{project_id}/pnl")
    cats = {b["category"]: float(b["amount"]) for b in r3.json()["cost_breakdown"]}
    assert "material" not in cats


async def test_margin_calculation(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    # Add revenue: paid invoice of 200000
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Service", "quantity": "1.00", "rate": "200000.00"},
            ],
        },
    )
    inv_id = r.json()["id"]
    await authed_admin_client.patch(f"/api/invoices/{inv_id}/status", json={"status": "sent"})
    await authed_admin_client.patch(f"/api/invoices/{inv_id}/status", json={"status": "paid"})
    # Add cost: 50000
    await authed_admin_client.post(
        f"/api/projects/{project_id}/costs",
        json={
            "project_id": str(project_id),
            "category": "material",
            "description": "Materials",
            "amount": "50000.00",
            "date": date.today().isoformat(),
        },
    )
    r2 = await authed_admin_client.get(f"/api/projects/{project_id}/pnl")
    pnl = r2.json()
    assert float(pnl["total_revenue"]) == 236000.0  # 200000 subtotal + 18% GST
    assert float(pnl["total_costs"]) == 50000.0
    assert float(pnl["net_profit"]) == 186000.0
    # margin = (186000 / 236000) * 100 = 78.81%
    assert float(pnl["margin_pct"]) == 78.81


async def test_pnl_non_billable_excluded(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    today = date.today()
    # Create non-billable entry
    await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": today.isoformat(),
            "hours": 8.0,
            "description": "Non-billable",
            "is_billable": False,
        },
    )
    # Create billable entry
    await authed_admin_client.post(
        "/api/time-entries",
        json={
            "project_id": project_id,
            "date": (today - timedelta(days=1)).isoformat(),
            "hours": 4.0,
            "description": "Billable",
            "is_billable": True,
        },
    )
    r = await authed_admin_client.get(f"/api/projects/{project_id}/pnl")
    pnl = r.json()
    # Only 4 billable hours * 5000 = 20000
    assert float(pnl["total_costs"]) == 20000.0
