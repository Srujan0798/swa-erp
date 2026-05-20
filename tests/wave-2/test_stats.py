import pytest

pytestmark = pytest.mark.asyncio


async def test_project_stats(authed_pm_client, db_session):
    r = await authed_pm_client.get("/api/projects/stats")
    assert r.status_code == 200
    body = r.json()
    assert "total_active" in body
    assert "by_status" in body
    assert "total_estimated_value" in body
    assert isinstance(body["by_status"], dict)