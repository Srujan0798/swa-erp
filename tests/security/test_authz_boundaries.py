"""Security boundaries: unauthenticated + under-privileged access is denied.

Pins the RBAC contract at the HTTP layer: 401 without credentials on a
protected route (REST semantics; deps.py raises 401 for missing creds, 403
for valid-cred-insufficient-role), 403 for viewer on a PM-only write, and
audit-log immutability (migration 0041).
"""

import pytest

pytestmark = pytest.mark.asyncio


async def test_protected_route_rejects_anonymous(client):
    r = await client.get("/api/projects")
    assert r.status_code == 401, r.text


async def test_metrics_rejects_anonymous(client):
    r = await client.get("/metrics")
    assert r.status_code == 401, r.text


async def test_viewer_cannot_create_project(authed_viewer_client):
    r = await authed_viewer_client.post(
        "/api/projects",
        json={"name": "Nope", "code": "NOPE-1", "client_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert r.status_code == 403, r.text


async def test_admin_can_create_project(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/clients",
        json={"name": "SecClient", "code": "SEC-001", "primary_email": "s@example.com"},
    )
    assert r.status_code == 201, r.text
    cid = r.json()["id"]
    r = await authed_admin_client.post(
        "/api/projects",
        json={"name": "SecProj", "code": "SEC-P-1", "client_id": cid},
    )
    assert r.status_code == 201, r.text


def test_audit_log_is_append_only(db_session):
    """DB trigger rejects UPDATE and DELETE on audit_log (migration 0041)."""
    import sqlalchemy as sa

    row_id = db_session.execute(
        sa.text(
            "INSERT INTO audit_log (action, entity_type) VALUES ('sec.probe', 'test') "
            "RETURNING id"
        )
    ).scalar_one()
    with pytest.raises(sa.exc.DBAPIError, match="append-only"):
        db_session.execute(
            sa.text("UPDATE audit_log SET action = 'sec.tampered' WHERE id = :i"),
            {"i": row_id},
        )
    db_session.rollback()
    # Rollback removed the probe row too — re-insert before the DELETE probe.
    row_id = db_session.execute(
        sa.text(
            "INSERT INTO audit_log (action, entity_type) VALUES ('sec.probe', 'test') "
            "RETURNING id"
        )
    ).scalar_one()
    with pytest.raises(sa.exc.DBAPIError, match="append-only"):
        db_session.execute(
            sa.text("DELETE FROM audit_log WHERE id = :i"), {"i": row_id}
        )
    db_session.rollback()


async def test_rate_limit_quota_headers_present(client_with_db, monkeypatch):
    """Allowed limited-path responses carry X-RateLimit-*; 429s add Retry-After."""
    import os

    if os.environ.get("DISABLE_AUTH_RATE_LIMIT", "").lower() in ("1", "true", "yes"):
        monkeypatch.delenv("DISABLE_AUTH_RATE_LIMIT", raising=False)
    from src.backend.core import rate_limit as rl_mod

    for lim in (rl_mod._upload_limiter, rl_mod._export_limiter, rl_mod._report_limiter):
        lim._buckets.clear()

    r = await client_with_db.post(
        "/api/auth/login", json={"email": "nobody@example.com", "password": "x"}
    )
    assert r.status_code in (401, 429)
    assert r.headers.get("X-RateLimit-Limit") is not None
    assert r.headers.get("X-RateLimit-Remaining") is not None
    assert r.headers.get("X-RateLimit-Reset") is not None
