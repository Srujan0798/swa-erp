"""Wave-48 production hardening tests.

1. Expensive-endpoint rate limiting: uploads 10/min, exports 20/min,
   reports 30/min per IP -> N+1th request returns 429 with Retry-After.
2. Dashboard endpoints stay unthrottled (read-heavy exclusion).
3. AuditLog rows on invoice create / status-change / delete.
"""
import uuid

from src.backend.models.audit_log import AuditLog


def _rate_limit_active(monkeypatch):
    import os

    if os.environ.get("DISABLE_AUTH_RATE_LIMIT", "").lower() in ("1", "true", "yes"):
        monkeypatch.delenv("DISABLE_AUTH_RATE_LIMIT", raising=False)


def _limiters():
    from src.backend.core import rate_limit as rl_mod

    return rl_mod._upload_limiter, rl_mod._export_limiter, rl_mod._report_limiter


async def test_export_rate_limit_triggers_on_21st_request(client_with_db, monkeypatch):
    """20 export requests pass the middleware; the 21st returns 429."""
    _rate_limit_active(monkeypatch)
    for lim in _limiters():
        lim._buckets.clear()
    statuses = []
    for _ in range(21):
        r = await client_with_db.get(
            "/api/exports/reports/financial.pdf?start_date=2024-01-01&end_date=2024-01-31"
        )
        statuses.append(r.status_code)
    assert 429 not in statuses[:20]
    assert statuses[20] == 429
    assert "Retry-After" in r.headers
    for lim in _limiters():
        lim._buckets.clear()


async def test_upload_rate_limit_triggers_on_11th_request(client_with_db, monkeypatch):
    """10 BOQ upload POSTs pass the middleware; the 11th returns 429."""
    _rate_limit_active(monkeypatch)
    for lim in _limiters():
        lim._buckets.clear()
    project_id = uuid.uuid4()
    statuses = []
    for _ in range(11):
        r = await client_with_db.post(
            f"/api/projects/{project_id}/boqs",
            files={"file": ("test.xlsx", b"fake", "application/octet-stream")},
        )
        statuses.append(r.status_code)
    assert 429 not in statuses[:10]
    assert statuses[10] == 429
    for lim in _limiters():
        lim._buckets.clear()


async def test_report_rate_limit_triggers_on_31st_request(client_with_db, monkeypatch):
    """30 report requests pass the middleware; the 31st returns 429."""
    _rate_limit_active(monkeypatch)
    for lim in _limiters():
        lim._buckets.clear()
    last = None
    for _ in range(31):
        last = await client_with_db.get("/api/reports/project-health")
    assert last.status_code == 429
    assert int(last.headers["Retry-After"]) >= 1
    for lim in _limiters():
        lim._buckets.clear()


async def test_dashboard_stays_unthrottled(client_with_db, monkeypatch):
    """Read-heavy dashboard KPI endpoint must never 429 (brief: do not throttle)."""
    _rate_limit_active(monkeypatch)
    for lim in _limiters():
        lim._buckets.clear()
    statuses = []
    for _ in range(35):
        r = await client_with_db.get("/api/dashboard/executive")
        statuses.append(r.status_code)
    assert 429 not in statuses
    for lim in _limiters():
        lim._buckets.clear()


async def _setup_project(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/clients",
        json={"name": "Audit Client", "code": f"AUDC-{uuid.uuid4().hex[:6]}",
              "primary_email": "audc@test.com"},
    )
    assert r.status_code == 201, r.text
    client_id = r.json()["id"]
    r2 = await authed_admin_client.post(
        "/api/projects",
        json={"client_id": str(client_id), "name": "Audit Project",
              "code": f"AUDP-{uuid.uuid4().hex[:6]}", "status": "Lead"},
    )
    assert r2.status_code == 201, r2.text
    return r2.json()["id"]


def _invoice_payload():
    return {"items": [{"description": "Svc", "quantity": "2.00", "rate": "1000.00"}]}


async def test_invoice_create_writes_audit_log(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices", json=_invoice_payload()
    )
    assert r.status_code == 201, r.text
    inv_id = r.json()["id"]
    rows = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "invoice.create", AuditLog.entity_type == "invoice")
        .all()
    )
    assert any(str(row.entity_id) == inv_id for row in rows)


async def test_invoice_status_change_writes_audit_log(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices", json=_invoice_payload()
    )
    inv_id = r.json()["id"]
    r2 = await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status", json={"status": "sent"}
    )
    assert r2.status_code == 200, r2.text
    row = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "invoice.status_change")
        .order_by(AuditLog.id.desc())
        .first()
    )
    assert row is not None
    assert str(row.entity_id) == inv_id
    assert row.before_json == {"status": "draft"}
    assert row.after_json == {"status": "sent"}


async def test_invoice_delete_writes_audit_log(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices", json=_invoice_payload()
    )
    inv_id = r.json()["id"]
    r2 = await authed_admin_client.delete(f"/api/invoices/{inv_id}")
    assert r2.status_code == 204, r2.text
    row = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "invoice.delete")
        .order_by(AuditLog.id.desc())
        .first()
    )
    assert row is not None
    assert str(row.entity_id) == inv_id
