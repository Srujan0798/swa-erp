"""Excel -> ERP importer.

Usage:
    python3 scripts/import_excel.py <sheet_type> <file.xlsx> [--commit]

sheet_type is one of: clients, inquiries, agreements, tokens,
document_references, projects, time_logs, sustainability.

Defaults to --dry-run (no writes). Use --commit to persist.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.backend.db.base import Base  # noqa: E402
from src.backend.db.session import SessionLocal, engine  # noqa: E402
from src.backend.services.import_service import SHEET_CONFIG, import_sheet  # noqa: E402

SHEET_TYPES = list(SHEET_CONFIG.keys())


def main() -> int:
    parser = argparse.ArgumentParser(description="Import an ERP Excel sheet.")
    parser.add_argument("sheet_type", choices=SHEET_TYPES)
    parser.add_argument("file", type=Path)
    parser.add_argument("--commit", action="store_true", help="Persist changes (default: dry-run).")
    parser.add_argument("--dry-run", action="store_true", help="Do not persist (default).")
    args = parser.parse_args()

    if not args.file.exists():
        print(json.dumps({"ok": False, "errors": [{"row": 0, "message": f"file not found: {args.file}"}]}))
        return 1

    # Ensure tables exist (covers Token / DocumentReference before their migration lands).
    Base.metadata.create_all(engine)

    session = SessionLocal()
    try:
        result = import_sheet(
            session, args.sheet_type, str(args.file), commit=args.commit
        )
    finally:
        session.close()

    print(json.dumps(result.to_dict(), indent=2, default=str))
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
