import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_project_health_200(authed_admin_client):
    r = await authed_admin_client.get("/api/reports/project-health")
    assert r.status_code == 200
    body = r.json()
    assert "by_status" in body
    assert "total_projects" in body
    assert "budget_variance_total" in body


async def test_utilization_200(authed_admin_client):
    r = await authed_admin_client.get("/api/reports/utilization")
    assert r.status_code == 200
    body = r.json()
    assert "period_start" in body
    assert "period_end" in body
    assert "members" in body


async def test_utilization_date_range(authed_admin_client):
    r = await authed_admin_client.get(
        "/api/reports/utilization",
        params={"start_date": "2026-01-01", "end_date": "2026-01-31"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["period_start"] == "2026-01-01"
    assert body["period_end"] == "2026-01-31"


async def test_revenue_200(authed_admin_client):
    r = await authed_admin_client.get("/api/reports/revenue")
    assert r.status_code == 200
    body = r.json()
    assert "monthly_revenue" in body
    assert "forecast" in body


async def test_client_summary_200(authed_admin_client):
    r = await authed_admin_client.get("/api/reports/client-summary")
    assert r.status_code == 200
    body = r.json()
    assert "clients" in body


async def test_executive_kpis_200(authed_admin_client):
    r = await authed_admin_client.get("/api/dashboard/executive")
    assert r.status_code == 200
    body = r.json()
    assert "active_projects" in body
    assert "pipeline_value" in body
    assert "avg_utilization" in body
    assert "overdue_tasks" in body
    assert "total_revenue_mtd" in body


async def test_unauthorized_401(client_with_db):
    endpoints = [
        "/api/reports/project-health",
        "/api/reports/utilization",
        "/api/reports/revenue",
        "/api/reports/client-summary",
        "/api/dashboard/executive",
    ]
    for endpoint in endpoints:
        r = await client_with_db.get(endpoint)
        assert r.status_code == 401, f"{endpoint} should return 401 without auth"


async def test_invalid_date_range_422(authed_admin_client):
    r = await authed_admin_client.get(
        "/api/reports/utilization",
        params={"start_date": "not-a-date"},
    )
    assert r.status_code == 422
