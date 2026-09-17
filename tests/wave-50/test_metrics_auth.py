"""Wave-50 task 01 (SF-4 / SEC-02): /metrics auth gate + METRICS_REQUIRE_AUTH.

- With the flag at its default (True), anonymous ``GET /metrics`` -> 401/403
  and an authenticated request -> 200 with Prometheus text.
- With the flag explicitly false, anonymous ``GET /metrics`` -> 200 (the
  trusted-internal-scraper escape hatch).
"""

import pytest

from src.backend.core.config import settings


@pytest.mark.asyncio
async def test_metrics_unauthenticated_rejected_by_default(client):
    assert settings.METRICS_REQUIRE_AUTH is True, "secure-by-default flag changed?"
    r = await client.get("/metrics")
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_metrics_authenticated_returns_prometheus_text(authed_admin_client):
    r = await authed_admin_client.get("/metrics")
    assert r.status_code == 200, f"/metrics returned {r.status_code}: {r.text}"
    assert "text/plain" in r.headers.get("content-type", "")
    assert "http_requests_total" in r.text


@pytest.mark.asyncio
async def test_metrics_open_when_flag_false(client, monkeypatch):
    monkeypatch.setattr(settings, "METRICS_REQUIRE_AUTH", False)
    r = await client.get("/metrics")
    assert r.status_code == 200, f"/metrics returned {r.status_code}: {r.text}"
    assert "http_requests_total" in r.text


@pytest.mark.asyncio
async def test_metrics_auth_restored_after_flag_reset(client, monkeypatch):
    """Toggling the flag is runtime-dynamic (guard reads settings per request)."""
    monkeypatch.setattr(settings, "METRICS_REQUIRE_AUTH", False)
    assert (await client.get("/metrics")).status_code == 200
    monkeypatch.setattr(settings, "METRICS_REQUIRE_AUTH", True)
    assert (await client.get("/metrics")).status_code in (401, 403)
