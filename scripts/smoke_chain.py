#!/usr/bin/env python3
"""Live API smoke of the core business chain.

Usage (stack must be up — backend on :8100 by default):

    python3 scripts/smoke_chain.py
    BASE_URL=http://localhost:8100 ADMIN_EMAIL=admin@swa.co.in ADMIN_PASSWORD=admin123! \\
        python3 scripts/smoke_chain.py

Exits 0 if the chain succeeds; non-zero with a clear error otherwise.
"""
from __future__ import annotations

import os
import sys
from datetime import date

import httpx

BASE = os.environ.get("BASE_URL", "http://localhost:8100").rstrip("/")
EMAIL = os.environ.get("ADMIN_EMAIL", "admin@swa.co.in")
PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123!")


def fail(msg: str, code: int = 1) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(code)


def main() -> None:
    print(f"Smoke chain against {BASE}")
    with httpx.Client(base_url=BASE, timeout=30.0) as c:
        try:
            r = c.get("/healthz")
        except httpx.ConnectError as e:
            fail(f"cannot connect — is backend up? ({e})")
        if r.status_code != 200:
            fail(f"/healthz → {r.status_code} {r.text}")
        print("  OK  healthz")

        r = c.post("/api/auth/login", json={"email": EMAIL, "password": PASSWORD})
        if r.status_code != 200:
            fail(
                f"login → {r.status_code} {r.text}\n"
                "  Hint: run APP_ENV=dev python3 scripts/seed_demo.py first"
            )
        token = r.json().get("access_token") or r.json().get("access")
        if not token:
            fail(f"login body missing access_token: {r.json()}")
        h = {"Authorization": f"Bearer {token}"}
        print(f"  OK  login as {EMAIL}")

        today = date.today().isoformat()
        r = c.post(
            "/api/inquiries",
            headers=h,
            json={
                "inquiry_date": today,
                "client_name": f"Smoke Client {today}",
                "requirement_summary": "smoke_chain.py auto test",
                "status": "New",
            },
        )
        if r.status_code not in (200, 201):
            fail(f"create inquiry → {r.status_code} {r.text}")
        inq = r.json()
        inq_id = inq.get("id")
        print(f"  OK  inquiry {inq.get('reference_id')}")

        r = c.post(
            f"/api/inquiries/{inq_id}/convert",
            headers=h,
            json={
                "project_name": f"Smoke Project {today}",
                "client_primary_email": f"smoke-{today}@example.com",
                "location": "Ahmedabad",
            },
        )
        if r.status_code not in (200, 201):
            fail(f"convert inquiry → {r.status_code} {r.text}")
        conv = r.json()
        client_id = (
            conv.get("converted_client_id")
            or conv.get("client_id")
            or (conv.get("client") or {}).get("id")
        )
        project_id = (
            conv.get("converted_project_id")
            or conv.get("project_id")
            or (conv.get("project") or {}).get("id")
        )
        print(f"  OK  convert → client={client_id} project={project_id}")

        if not client_id:
            # list clients as fallback
            r = c.get("/api/clients", headers=h)
            if r.status_code == 200:
                items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
                if items:
                    client_id = items[0].get("id")

        if not client_id:
            fail("no client_id after convert")

        r = c.post(
            "/api/service-agreements",
            headers=h,
            json={
                "client_id": client_id,
                "service_name": "INSUDESIGN",
                "start_date": today,
                "status": "Active",
            },
        )
        if r.status_code not in (200, 201):
            fail(f"service agreement → {r.status_code} {r.text}")
        sa = r.json()
        sa_id = sa.get("id")
        print(f"  OK  agreement {sa.get('reference_id')} (INSUDESIGN)")

        r = c.post(
            "/api/tokens",
            headers=h,
            json={
                "agreement_id": sa_id,
                "token_date": today,
                "description": "smoke token",
                "project_id": project_id,
            },
        )
        if r.status_code not in (200, 201):
            fail(f"token → {r.status_code} {r.text}")
        tkn = r.json()
        print(f"  OK  token {tkn.get('reference_id')}")

        if project_id:
            r = c.post(
                "/api/document-references",
                headers=h,
                json={
                    "project_id": project_id,
                    "token_id": tkn.get("id"),
                    "doc_date": today,
                    "document_type": "DBR",
                    "description": "smoke DBR",
                },
            )
            if r.status_code not in (200, 201):
                fail(f"document reference → {r.status_code} {r.text}")
            dbr = r.json()
            print(f"  OK  doc ref {dbr.get('reference_id')}")
        else:
            print("  SKIP doc ref (no project_id)")

    print("\n✅ smoke_chain PASSED")


if __name__ == "__main__":
    main()
