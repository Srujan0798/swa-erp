"""Idempotency keys on money-moving invoice POSTs (migration 0042).

- Same key + same body: second request replays the first response
  (Idempotent-Replayed header) and creates no duplicate invoice.
- Same key + different body: 422 (client bug signal).
- No key: normal behavior, unchanged.
- PK is composite (key, user_id) (migration 0043): different users sharing
  a key are independent; a lost insert race replays the stored response.
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from src.backend.models.idempotency_key import IdempotencyKey
from src.backend.services.idempotency_service import hash_request, replay_or_execute

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


async def test_different_users_same_key_independent(authed_admin_client, authed_pm_client):
    """Composite PK (key, user_id): two users sharing a key never collide."""
    project_id = await _setup_project(authed_admin_client)
    key = f"idem-{uuid.uuid4().hex}"
    headers = {"Idempotency-Key": key}

    r1 = await authed_pm_client.post(
        f"/api/projects/{project_id}/invoices", json=ITEMS, headers=headers
    )
    assert r1.status_code == 201, r1.text
    assert "Idempotent-Replayed" not in r1.headers

    r2 = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices", json=ITEMS, headers=headers
    )
    assert r2.status_code == 201, r2.text
    assert r2.headers.get("Idempotent-Replayed") != "true"
    assert r2.json()["id"] != r1.json()["id"]


async def test_lost_insert_race_replays_stored_response(db_session, pm_user):
    """A concurrent writer claiming (key, user) first must not 500: the loser
    replays the winner's stored response (IntegrityError -> re-select)."""
    key = "race-loser"
    path = "/api/projects/00000000-0000-0000-0000-000000000000/invoices"
    req_hash = hash_request("POST", path, "{}")
    expires_at = datetime.now(UTC) + timedelta(hours=24)

    def _claim_first():
        db_session.add(
            IdempotencyKey(
                key=key,
                user_id=pm_user.id,
                method="POST",
                path=path,
                request_hash=req_hash,
                status_code=201,
                response_body={"won": True},
                expires_at=expires_at,
            )
        )
        db_session.flush()
        return 201, {"won": True}

    status_code, body, replayed = replay_or_execute(
        db_session,
        key=key,
        user_id=pm_user.id,
        method="POST",
        path=path,
        request_hash=req_hash,
        execute=_claim_first,
    )
    assert replayed is True
    assert (status_code, body) == (201, {"won": True})
