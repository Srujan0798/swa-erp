#!/usr/bin/env python3
"""Full internship bootstrap: REAL Excel → DB → linked core chain for UI.

1. Wipe domain tables
2. Import all real sheets from resources/
3. Link converted inquiries → clients → projects (so Projects page is not empty stubs)
4. Ensure login users for all roles

Usage:
  APP_ENV=dev python3 scripts/bootstrap_real.py
"""
from __future__ import annotations

import os
import sys
from datetime import date
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
from src.backend.services.reference_id_service import generate_reference_id  # noqa: E402

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
    ("pm@swa.co.in", "Priya Mehta", "pm", "pm123!"),
    ("designer@swa.co.in", "Rahul Sharma", "designer", "designer123!"),
    ("auditor@swa.co.in", "Ankit Desai", "auditor", "auditor123!"),
    ("viewer@swa.co.in", "Neha Gupta", "viewer", "viewer123!"),
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
    """Make converted inquiries land on real clients + projects for the UI."""
    clients = list(s.scalars(select(Client)).all())
    by_name = {_norm(c.name): c for c in clients}
    # also strip trailing spaces variants
    for c in clients:
        by_name[_norm(c.name.strip())] = c

    inquiries = list(s.scalars(select(Inquiry)).all())
    created_projects = 0
    linked = 0

    for inq in inquiries:
        client = by_name.get(_norm(inq.client_name))
        if client is None:
            # fuzzy: first word match
            cn = _norm(inq.client_name)
            for name, c in by_name.items():
                if cn and (cn in name or name in cn or cn.split()[0] in name):
                    client = c
                    break
        if client is None and inq.client_name:
            # create client from inquiry so UI shows the inquiry's real client name
            code = generate_reference_id(s, "CLT")
            # generate_reference_id commits; re-open entity
            client = Client(
                code=code,
                name=inq.client_name.strip(),
                primary_email=f"import+{code.lower().replace(' ', '-')}@swa.internal",
                country="India",
                client_status="Active",
                is_active=True,
                industry=None,
                notes=f"Created from inquiry {inq.reference_id}",
            )
            s.add(client)
            s.flush()
            by_name[_norm(client.name)] = client
            print(f"  + client from inquiry: {client.code} {client.name}")

        if client is None:
            continue

        # find or create a project for this inquiry
        project = None
        if inq.converted_project_id:
            project = s.get(Project, inq.converted_project_id)
        if project is None:
            # one project per inquiry reference
            existing = s.scalar(
                select(Project).where(
                    Project.client_id == client.id,
                    Project.name.ilike(f"%{inq.reference_id}%"),
                )
            )
            project = existing
        if project is None:
            pcode = generate_reference_id(s, "PRJ")
            summary = (inq.requirement_summary or "Imported project")[:200]
            project = Project(
                code=pcode,
                client_id=client.id,
                name=f"{summary} ({inq.reference_id})",
                description=inq.requirement_summary,
                status="Awarded" if (inq.status or "").lower() == "converted" else "Lead",
                estimated_value=inq.estimated_value,
                start_date=inq.inquiry_date or date.today(),
                is_active=True,
            )
            s.add(project)
            s.flush()
            created_projects += 1
            print(f"  + project {project.code} for {client.name}")

        inq.converted_client_id = client.id
        inq.converted_project_id = project.id
        if (inq.status or "").lower() == "converted" or inq.status == "Converted":
            inq.status = "Converted"
        if client.first_inquiry_id is None:
            client.first_inquiry_id = inq.id
        linked += 1

    # Attach tokens' agreements clients: ensure each SA client has at least one project
    for sa in s.scalars(select(ServiceAgreement)).all():
        has_proj = s.scalar(
            select(Project).where(Project.client_id == sa.client_id).limit(1)
        )
        if has_proj is None:
            pcode = generate_reference_id(s, "PRJ")
            project = Project(
                code=pcode,
                client_id=sa.client_id,
                name=f"{sa.service_name} work ({sa.reference_id})",
                description=f"Project under agreement {sa.reference_id}",
                status="Design",
                start_date=sa.start_date,
                is_active=True,
            )
            s.add(project)
            s.flush()
            created_projects += 1
            # link tokens without project
            for tkn in s.scalars(
                select(Token).where(Token.agreement_id == sa.id)
            ).all():
                if tkn.project_id is None:
                    tkn.project_id = project.id

    s.commit()
    print(f"Linked {linked} inquiries; created {created_projects} projects for UI.")


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
        for sheet_type, filename in ORDER:
            path = BASE / filename
            if not path.exists():
                print(f"  SKIP missing {filename}")
                continue
            # allow_stubs: real multi-sheet sets create SWA-SYS-UNLINKED /
            # orphan projects when Project Tracking lags cross-sheet refs.
            result = import_sheet(
                s, sheet_type, str(path), commit=True, allow_stubs=True
            )
            d = result.to_dict()
            status = "OK" if d["ok"] else "ERR"
            print(
                f"  {status} {sheet_type:22} rows={d['total_rows']:3} "
                f"+{d['created']} ~{d['updated']} !{len(d['errors'])}"
            )
            for e in d["errors"][:3]:
                print(f"       {e}")
        print("=== 4. Link inquiry → client → project ===")
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
        print("DONE. Open http://127.0.0.1:3100  (NOT :3000 — that is Open WebUI)")
        print("Login: admin@swa.co.in / admin123!")
        return 0
    finally:
        s.close()


if __name__ == "__main__":
    raise SystemExit(main())
