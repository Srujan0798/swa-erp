#!/usr/bin/env python3
"""Bootstrap source Excel rows without synthesizing clients or projects.

1. Wipe domain tables
2. Import all real sheets from resources/ with strict foreign-key resolution
3. Link inquiries to uniquely matching existing clients
4. Ensure the administrator login

Usage:
  APP_ENV=dev python3 scripts/bootstrap_real.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("APP_ENV", "dev")
os.environ.setdefault("DATABASE_URL", "postgresql://swa:swa@localhost:5432/swa_erp")

from sqlalchemy import select, text  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from src.backend.core.security import hash_password  # noqa: E402
from src.backend.db.session import SessionLocal  # noqa: E402
from src.backend.models import (  # noqa: E402
    Client,
    Inquiry,
    Project,
    ServiceAgreement,
    Token,
    User,
)
from src.backend.services.import_service import import_sheet  # noqa: E402

BASE = ROOT / "resources" / "ERP_Sheets_Extracted" / "ERP Sheets"
ORDER = [
    ("inquiries", "Inquiries Sheet.xlsx"),
    ("clients", "Clients Sheet.xlsx"),
    ("agreements", "Service Agreements Sheet.xlsx"),
    ("projects", "Project Tracking Sheet.xlsx"),
    ("tokens", "Tokens Sheet.xlsx"),
    ("document_references", "Document Reference Sheet.xlsx"),
    ("time_logs", "Time Logging Sheet.xlsx"),
    ("sustainability", "Sustainability Metrics Sheet.xlsx"),
]

USERS = [
    ("admin@swa.co.in", "Admin SWA", "admin", "admin123!"),
]


def wipe(s: Session) -> None:
    for t in (
        "time_entries",
        "sustainability_metrics",
        "document_references",
        "tokens",
        "service_agreements",
        "inquiries",
        "projects",
        "contacts",
        "clients",
        "reference_counters",
    ):
        s.execute(text(f"TRUNCATE {t} CASCADE"))
    s.commit()
    print("Wiped domain tables.")


def ensure_users(s: Session) -> None:
    for email, name, role, password in USERS:
        u = s.scalar(select(User).where(User.email == email))
        if u is None:
            s.add(
                User(
                    email=email,
                    name=name,
                    role=role,
                    password_hash=hash_password(password),
                    is_active=True,
                )
            )
            print(f"  + user {email} / {password}")
        else:
            u.password_hash = hash_password(password)
            u.role = role
            u.is_active = True
            print(f"  ~ user {email} password reset")
    s.commit()


def _norm(name: str | None) -> str:
    return " ".join((name or "").lower().split())


def link_chain(s: Session) -> None:
    clients = list(s.scalars(select(Client).where(Client.deleted_at.is_(None))).all())
    by_name: dict[str, list[Client]] = {}
    for client in clients:
        by_name.setdefault(_norm(client.name), []).append(client)

    linked = 0
    inquiries = s.scalars(select(Inquiry).where(Inquiry.deleted_at.is_(None))).all()
    for inquiry in inquiries:
        matches = by_name.get(_norm(inquiry.client_name), [])
        if len(matches) != 1 or inquiry.converted_client_id is not None:
            continue
        inquiry.converted_client_id = matches[0].id
        linked += 1

    s.commit()
    print(f"Linked {linked} inquiries to existing clients; no projects synthesized.")


def main() -> int:
    if not BASE.is_dir():
        print(f"Missing sheets dir: {BASE}", file=sys.stderr)
        return 1

    s = SessionLocal()
    try:
        print("=== 1. Wipe ===")
        wipe(s)
        print("=== 2. Users ===")
        ensure_users(s)
        print("=== 3. Import real Excel ===")
        failed = False
        for sheet_type, filename in ORDER:
            path = BASE / filename
            if not path.exists():
                print(f"  SKIP missing {filename}")
                failed = True
                continue
            result = import_sheet(
                s, sheet_type, str(path), commit=True, allow_stubs=False
            )
            d = result.to_dict()
            if not d["ok"]:
                failed = True
            status = "OK" if d["ok"] else "ERR"
            print(
                f"  {status} {sheet_type:22} rows={d['total_rows']:3} "
                f"+{d['created']} ~{d['updated']} !{len(d['errors'])}"
            )
            for e in d["errors"][:3]:
                print(f"       {e}")
        print("=== 4. Link inquiries to existing clients ===")
        link_chain(s)
        print("=== 5. Counts ===")
        for label, model in [
            ("users", User),
            ("clients", Client),
            ("inquiries", Inquiry),
            ("projects", Project),
            ("agreements", ServiceAgreement),
            ("tokens", Token),
        ]:
            print(f"  {label:12} {s.query(model).count()}")
        print()
        if failed:
            print("Import incomplete: resolve missing sheets or references and re-import.")
            return 1
        print("DONE. Open http://127.0.0.1:3100  (NOT :3000 — that is Open WebUI)")
        print("Login: admin@swa.co.in / admin123!")
        return 0
    finally:
        s.close()


if __name__ == "__main__":
    raise SystemExit(main())
