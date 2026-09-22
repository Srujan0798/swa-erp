"""Integration: core ID chain end-to-end through the API.

Inquiry -> Client -> Project -> Service Agreement -> Token, asserting the
SWA-{year}-{TYPE}-{seq} reference-ID contract at each step.
"""

import re

import pytest

pytestmark = pytest.mark.asyncio

REF = re.compile(r"^SWA-\d{4}-[A-Z]+-\d{3,}$")


async def test_core_id_chain_end_to_end(authed_admin_client):
    # Inquiry
    r = await authed_admin_client.post(
        "/api/inquiries",
        json={
            "inquiry_date": "2025-06-01",
            "client_name": "Chain Corp",
            "requirement_summary": "Full chain test",
        },
    )
    assert r.status_code == 201, r.text
    inquiry = r.json()
    assert REF.match(inquiry["reference_id"]), inquiry["reference_id"]

    # Convert -> client + project
    r = await authed_admin_client.post(
        f"/api/inquiries/{inquiry['id']}/convert", json={"project_name": "Chain Project"}
    )
    assert r.status_code in (200, 201), r.text
    converted = r.json()
    client_id = converted["client_id"]
    project_id = converted["project_id"]

    # Client created (business key is `code`; CLT sequence feeds it)
    r = await authed_admin_client.get(f"/api/clients/{client_id}")
    assert r.status_code == 200, r.text
    assert r.json()["code"]

    # Service agreement on client (references the converted inquiry)
    r = await authed_admin_client.post(
        "/api/service-agreements",
        json={
            "client_id": client_id,
            "inquiry_id": inquiry["id"],
            "service_name": "Design",
            "start_date": "2025-06-01",
            "total_tokens": 10,
        },
    )
    assert r.status_code == 201, r.text
    agreement = r.json()
    assert REF.match(agreement["reference_id"]), agreement["reference_id"]

    # Token under agreement
    r = await authed_admin_client.post(
        "/api/tokens",
        json={
            "agreement_id": agreement["id"],
            "token_date": "2025-06-02",
            "description": "Chain token",
        },
    )
    assert r.status_code == 201, r.text
    assert REF.match(r.json()["reference_id"])
