#!/usr/bin/env python3
"""Import REAL SWA Excel sheets from resources/ (not demo seed).

Default is dry-run. Pass --commit to write.

Order respects FKs:
  inquiries → clients → agreements → projects → tokens →
  document_references → time_logs → sustainability

Usage:
  python3 scripts/import_real_sheets.py
  python3 scripts/import_real_sheets.py --commit
  python3 scripts/import_real_sheets.py --commit --wipe
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

BASE = ROOT / "resources" / "ERP_Sheets_Extracted" / "ERP Sheets"

ORDER: list[tuple[str, str]] = [
    ("inquiries", "Inquiries Sheet.xlsx"),
    ("clients", "Clients Sheet.xlsx"),
    ("agreements", "Service Agreements Sheet.xlsx"),
    ("projects", "Project Tracking Sheet.xlsx"),
    ("tokens", "Tokens Sheet.xlsx"),
    ("document_references", "Document Reference Sheet.xlsx"),
    ("time_logs", "Time Logging Sheet.xlsx"),
    ("sustainability", "Sustainability Metrics Sheet.xlsx"),
]


def _wipe(session) -> None:
    from sqlalchemy import text

    tables = [
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
    ]
    for t in tables:
        session.execute(text(f"TRUNCATE {t} CASCADE"))
    session.commit()
    print("Wiped domain tables (users kept).")


def _ensure_admin(session) -> None:
    from sqlalchemy import select

    from src.backend.core.security import hash_password
    from src.backend.models.user import User

    email = "admin@swa.co.in"
    user = session.scalar(select(User).where(User.email == email))
    if user is None:
        session.add(
            User(
                email=email,
                name="Admin",
                role="admin",
                password_hash=hash_password("admin123!"),
                is_active=True,
            )
        )
        session.commit()
        print(f"Created login user {email} / admin123!")


def main() -> int:
    parser = argparse.ArgumentParser(description="Import real SWA Excel sheets.")
    parser.add_argument("--commit", action="store_true", help="Persist (default dry-run).")
    parser.add_argument(
        "--wipe",
        action="store_true",
        help="TRUNCATE core domain tables before import (requires --commit).",
    )
    parser.add_argument(
        "--base",
        type=Path,
        default=BASE,
        help="Directory containing the xlsx files",
    )
    args = parser.parse_args()

    if args.wipe and not args.commit:
        print("Refusing --wipe without --commit", file=sys.stderr)
        return 2

    os.environ.setdefault("APP_ENV", "dev")

    from src.backend.db.session import SessionLocal
    from src.backend.services.import_service import import_sheet

    if not args.base.is_dir():
        print(f"Sheet directory not found: {args.base}", file=sys.stderr)
        return 1

    session = SessionLocal()
    try:
        if args.wipe:
            _wipe(session)
        _ensure_admin(session)

        summary = []
        failed = False
        for sheet_type, filename in ORDER:
            path = args.base / filename
            if not path.exists():
                summary.append({"sheet_type": sheet_type, "ok": False, "errors": [{"message": f"missing {path}"}]})
                failed = True
                continue
            result = import_sheet(session, sheet_type, str(path), commit=args.commit)
            d = result.to_dict()
            summary.append(d)
            flag = "OK " if d["ok"] else "ERR"
            print(
                f"{flag} {sheet_type:22} total={d['total_rows']:3} "
                f"created={d['created']:3} updated={d['updated']:3} "
                f"skipped={d['skipped']:3} errors={len(d['errors'])}"
            )
            for e in d["errors"][:5]:
                print(f"     · {e}")
            if not d["ok"]:
                failed = True

        print(json.dumps({"commit": args.commit, "summary": summary}, indent=2, default=str))
        if args.commit and not failed:
            print("\nReal Excel data committed. Login: admin@swa.co.in / admin123!")
        elif not args.commit:
            print("\nDry-run only. Re-run with --commit to write.")
        return 1 if failed else 0
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
