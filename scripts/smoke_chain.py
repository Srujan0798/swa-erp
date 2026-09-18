#!/usr/bin/env python3
"""Live API smoke of the core business chain.

WARNING: this script writes real rows (client, project, agreement, token, DBR,
time entry, invoice) into whatever database the backend on :8100 is serving.
It does NOT clean up after itself — the local DB gets polluted with each run.
Afterwards run `make swa-live-local` to reset to the real SWA dataset.

Usage (stack must be up — backend on :8100 by default):

    python3 scripts/smoke_chain.py
    BASE_URL=http://localhost:8100 ADMIN_EMAIL=admin@swa.co.in ADMIN_PASSWORD=admin123! \
        python3 scripts/smoke_chain.py

Exits 0 if the chain succeeds; non-zero with a clear error otherwise.
"""

from __future__ import annotations

import os
import sys
import uuid
from datetime import date

import httpx

BASE = os.environ.get("BASE_URL", "http://localhost:8100").rstrip("/")
EMAIL = os.environ.get("ADMIN_EMAIL", "admin@swa.co.in")
PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123!")

RUN = uuid.uuid4().hex[:8]


def fail(msg: str, code: int = 1) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(code)


def expect(r: httpx.Response, label: str, ok: tuple[int, ...], show: bool = True) -> httpx.Response:
    if r.status_code not in ok:
        fail(f"{label} → {r.status_code} {r.text}")
    if show:
        print(f"  OK  {label}")
    return r


def main() -> None:
    print("=" * 60)
    print("WARNING: smoke_chain writes test data into the live local DB and")
    print("does not clean up. Run `make swa-live-local` afterwards to reset.")
    print("=" * 60)
    print(f"Smoke chain against {BASE}")
    with httpx.Client(base_url=BASE, timeout=30.0) as c:
        try:
            r = c.get("/healthz")
        except httpx.ConnectError as e:
            fail(f"cannot connect — is backend up? ({e})")
        expect(r, "healthz", (200,), show=False)
        print("  OK  healthz")

        r = c.post("/api/auth/login", json={"email": EMAIL, "password": PASSWORD})
        if r.status_code != 200:
            fail(f"login → {r.status_code} {r.text}")
        token = r.json().get("access_token") or r.json().get("access")
        if not token:
            fail(f"login body missing access_token: {r.json()}")
        h = {"Authorization": f"Bearer {token}"}
        print(f"  OK  login as {EMAIL}")

        today = date.today().isoformat()
        client_name = f"Smoke Client {RUN}"
        project_name = f"Smoke Project {RUN}"
        r = c.post(
            "/api/inquiries",
            headers=h,
            json={
                "inquiry_date": today,
                "client_name": client_name,
                "requirement_summary": "smoke_chain.py auto test",
                "status": "New",
            },
        )
        expect(r, "create inquiry", (200, 201))
        inq = r.json()
        inq_id = inq.get("id")
        print(f"  OK  inquiry {inq.get('reference_id')}")

        r = expect(
            c.post(
                f"/api/inquiries/{inq_id}/convert",
                headers=h,
                json={
                    "project_name": project_name,
                    "client_primary_email": f"smoke-{RUN}@example.com",
                    "location": "Ahmedabad",
                },
            ),
            "convert inquiry",
            (200, 201),
        )
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
        if not client_id or not project_id:
            fail(f"convert did not return client_id and project_id: {conv}")
        print(f"  OK  convert → client={client_id} project={project_id}")

        r = expect(c.get(f"/api/clients/{client_id}", headers=h), "GET client", (200,))
        client_code = r.json().get("code")
        if not client_code or not client_code.startswith("SWA-") or "-CLT-" not in client_code:
            fail(f"client code is not a SWA CLT id: {client_code!r}")
        r = expect(c.get(f"/api/projects/{project_id}", headers=h), "GET project", (200,))
        project_code = r.json().get("code")
        if not project_code or not project_code.startswith("SWA-") or "-PRJ-" not in project_code:
            fail(f"project code is not a SWA PRJ id: {project_code!r}")
        print(f"  OK  SWA ids: client={client_code} project={project_code}")

        r = expect(
            c.post(
                "/api/service-agreements",
                headers=h,
                json={
                    "client_id": client_id,
                    "service_name": "INSUDESIGN",
                    "start_date": today,
                    "status": "Active",
                },
            ),
            "service agreement",
            (200, 201),
        )
        sa = r.json()
        sa_id = sa.get("id")
        print(f"  OK  agreement {sa.get('reference_id')} (INSUDESIGN)")

        r = expect(
            c.post(
                "/api/tokens",
                headers=h,
                json={
                    "agreement_id": sa_id,
                    "token_date": today,
                    "description": "smoke token",
                    "project_id": project_id,
                },
            ),
            "token",
            (200, 201),
        )
        tkn = r.json()
        print(f"  OK  token {tkn.get('reference_id')}")

        r = expect(
            c.post(
                "/api/document-references",
                headers=h,
                json={
                    "project_id": project_id,
                    "token_id": tkn.get("id"),
                    "doc_date": today,
                    "document_type": "DBR",
                    "description": "smoke DBR",
                },
            ),
            "document reference",
            (200, 201),
        )
        print(f"  OK  doc ref {r.json().get('reference_id')}")

        r = expect(
            c.post(
                "/api/time-entries",
                headers=h,
                json={
                    "project_id": project_id,
                    "date": today,
                    "hours": 1.0,
                    "description": "smoke time",
                    "is_billable": True,
                },
            ),
            "time entry 1h",
            (200, 201),
        )

        r = expect(
            c.post(
                f"/api/projects/{project_id}/invoices/generate-from-time",
                headers=h,
                json={"start_date": today, "end_date": today},
            ),
            "generate invoice from time",
            (200, 201),
        )
        inv = r.json()
        items = inv.get("items", [])
        if len(items) != 1 or not items[0].get("time_entry_id"):
            fail(f"expected 1 time-linked item, got: {items}")
        rate = items[0].get("rate")
        qty = items[0].get("quantity")
        if not rate or float(qty) * float(rate) != 5000.0:
            fail(f"expected 1h @ 5000/h = 5000.00, got {qty}h @ {rate}")
        subtotal = float(inv["subtotal"])
        gst = float(inv["gst_amount"])
        total = float(inv["total"])
        if subtotal != 5000.0 or gst != 900.0 or total != 5900.0:
            fail(f"expected 5000.00 + 18% GST 900.00 = 5900.00 INR, got {subtotal}/{gst}/{total}")
        if inv.get("currency") != "INR" or inv.get("status") != "draft":
            fail(f"expected INR draft invoice, got {inv.get('currency')}/{inv.get('status')}")
        print(f"  OK  invoice {inv['invoice_number']} 5000.00 + GST18 900.00 = 5900.00 INR")

        inv_id = inv["id"]
        for status_name in ("sent", "paid"):
            r = expect(
                c.patch(f"/api/invoices/{inv_id}/status", headers=h, json={"status": status_name}),
                f"invoice → {status_name}",
                (200,),
            )
        if r.json().get("status") != "paid" or not r.json().get("paid_at"):
            fail(f"expected paid invoice with paid_at, got: {r.json()}")

        r = expect(
            c.post(
                f"/api/projects/{project_id}/invoices/generate-from-time",
                headers=h,
                json={"start_date": today, "end_date": today},
            ),
            "regenerate must be rejected",
            (400,),
        )

    print("\n✅ smoke_chain PASSED")


if __name__ == "__main__":
    main()
