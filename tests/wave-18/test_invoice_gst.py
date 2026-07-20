"""Wave-18 dedicated invoice GST tests.

Focuses only on the GST breakdown aspect of invoices; the broader invoice
tests in tests/wave-7/test_invoicing.py remain the canonical suite.
"""
from decimal import Decimal

import pytest

pytestmark = pytest.mark.asyncio


async def _setup_project(authed_admin_client, name="GST2-Client", code="GST2C-1"):
    r = await authed_admin_client.post(
        "/api/clients",
        json={"name": name, "code": code, "primary_email": f"{code}@test.com"},
    )
    assert r.status_code == 201
    client_id = r.json()["id"]
    r2 = await authed_admin_client.post(
        "/api/projects",
        json={
            "client_id": str(client_id),
            "name": f"{name} Project",
            "code": f"{code}P",
            "status": "Lead",
        },
    )
    assert r2.status_code == 201
    return r2.json()["id"]


async def test_gst_included_in_total_amount(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [{"description": "svc", "quantity": "1.00", "rate": "1000.00"}],
        },
    )
    assert r.status_code == 201
    inv = r.json()
    assert Decimal(str(inv["subtotal"])) + Decimal(str(inv["gst_amount"])) == Decimal(
        str(inv["total"])
    )


async def test_gst_zero_when_no_items(authed_admin_client, db_session):
    """Edge: empty items list rejected at schema level (min_length=1)."""
    project_id = await _setup_project(authed_admin_client, name="NoItems", code="NI-1")
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={"items": []},
    )
    assert r.status_code == 422


async def test_gst_default_when_tax_rate_omitted(authed_admin_client, db_session):
    """If tax_rate is omitted entirely, default 18% should apply."""
    project_id = await _setup_project(authed_admin_client, name="Default", code="DEF-1")
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [{"description": "x", "quantity": "1.00", "rate": "100.00"}],
        },
    )
    assert r.status_code == 201
    inv = r.json()
    assert Decimal(str(inv["gst_percent"])) == Decimal("18.00")
    assert Decimal(str(inv["gst_amount"])) == Decimal("18.00")
    assert Decimal(str(inv["total"])) == Decimal("118.00")


async def test_gst_line_in_list_view(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client, name="ListView", code="LV-1")
    await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={"items": [{"description": "x", "quantity": "1.00", "rate": "100.00"}]},
    )
    r = await authed_admin_client.get(f"/api/projects/{project_id}/invoices")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) >= 1
    first = items[0]
    assert "gst_amount" in first
    assert "gst_percent" in first
    assert Decimal(str(first["gst_amount"])) == Decimal("18.00")
