"""Idempotency keys on money-moving invoice POSTs (migration 0042).

- Same key + same body: second request replays the first response
  (Idempotent-Replayed header) and creates no duplicate invoice.
- Same key + different body: 422 (client bug signal).
- No key: normal behavior, unchanged.
"""

import uuid

import pytest

pytestmark = pytest.mark.asyncio

ITEMS = {"items": [{"description": "Design", "quantity": "2.00", "rate": "5000.00"}]}


async def _setup_project(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/clients",
        json={"name": "IdemClient", "code": f"IDM-{uuid.uuid4().hex[:6]}", "primary_email": "i@example.com"},
    )
    cid = r.json()["id"]
    r = await authed_admin_client.post(
        "/api/projects", json={"name": "IdemProj", "code": f"IDM-{uuid.uuid4().hex[:6]}", "client_id": cid}
    )
    return r.json()["id"]


async def test_create_replay_no_duplicate(authed_admin_client, authed_pm_client):
    project_id = await _setup_project(authed_admin_client)
    key = f"idem-{uuid.uuid4().hex}"
    headers = {"Idempotency-Key": key}

    r1 = await authed_pm_client.post(
        f"/api/projects/{project_id}/invoices", json=ITEMS, headers=headers
    )
    assert r1.status_code == 201, r1.text
    assert "Idempotent-Replayed" not in r1.headers

    r2 = await authed_pm_client.post(
        f"/api/projects/{project_id}/invoices", json=ITEMS, headers=headers
    )
    assert r2.status_code == 201, r2.text
    assert r2.headers.get("Idempotent-Replayed") == "true"
    assert r2.json()["id"] == r1.json()["id"]

    listed = await authed_pm_client.get(f"/api/projects/{project_id}/invoices")
    assert listed.json()["total"] == 1


async def test_same_key_different_body_rejected(authed_admin_client, authed_pm_client):
    project_id = await _setup_project(authed_admin_client)
    key = f"idem-{uuid.uuid4().hex}"
    headers = {"Idempotency-Key": key}

    r1 = await authed_pm_client.post(
        f"/api/projects/{project_id}/invoices", json=ITEMS, headers=headers
    )
    assert r1.status_code == 201, r1.text

    other = {"items": [{"description": "Other", "quantity": "1.00", "rate": "999.00"}]}
    r2 = await authed_pm_client.post(
        f"/api/projects/{project_id}/invoices", json=other, headers=headers
    )
    assert r2.status_code == 422, r2.text


async def test_status_update_replay(authed_admin_client, authed_pm_client):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_pm_client.post(f"/api/projects/{project_id}/invoices", json=ITEMS)
    assert r.status_code == 201, r.text
    invoice_id = r.json()["id"]

    key = f"idem-{uuid.uuid4().hex}"
    headers = {"Idempotency-Key": key}
    body = {"status": "sent"}
    r1 = await authed_pm_client.patch(
        f"/api/invoices/{invoice_id}/status", json=body, headers=headers
    )
    assert r1.status_code == 200, r1.text
    r2 = await authed_pm_client.patch(
        f"/api/invoices/{invoice_id}/status", json=body, headers=headers
    )
    assert r2.status_code == 200, r2.text
    assert r2.headers.get("Idempotent-Replayed") == "true"
    assert r2.json()["status"] == "sent"


async def test_no_key_behaves_normally(authed_admin_client, authed_pm_client):
    project_id = await _setup_project(authed_admin_client)
    r1 = await authed_pm_client.post(f"/api/projects/{project_id}/invoices", json=ITEMS)
    r2 = await authed_pm_client.post(f"/api/projects/{project_id}/invoices", json=ITEMS)
    assert r1.status_code == 201 and r2.status_code == 201
    assert r1.json()["id"] != r2.json()["id"]
