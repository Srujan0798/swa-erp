"""Wave 13 — Excel import tooling tests.

These exercise src.backend.services.import_service against synthetic fixtures
in tests/wave-13/fixtures/ (no real client data). The CLI smoke test runs the
real script against an isolated SQLite file.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.models import (
    Client,
    DocumentReference,
    Inquiry,
    Project,
    ServiceAgreement,
    SustainabilityMetric,
    TimeEntry,
    Token,
)
from src.backend.services.import_service import import_sheet

FIX = Path(__file__).parent / "fixtures"
REPO = Path(__file__).parent.parent.parent


def _seed_core(db):
    client = Client(
        code="SWA-2025-CLT-001",
        name="Acme Corp",
        primary_email="acme@example.com",
    )
    db.add(client)
    db.flush()
    db.add(
        Inquiry(
            reference_id="SWA-2025-INQ-001",
            inquiry_date=date.today(),
            client_name="Acme Corp",
            status="New",
        )
    )
    db.add(
        ServiceAgreement(
            reference_id="SWA-2025-SA-011",
            client_id=client.id,
            service_name="INSUDESIGN",
            start_date=date.today(),
        )
    )
    db.add(Project(code="SWA-2025-PRJ-065", client_id=client.id, name="Green Tower"))
    db.commit()


# --------------------------------------------------------------------------- #
# Per-sheet happy paths
# --------------------------------------------------------------------------- #
def test_import_clients_creates(seeded):
    r = import_sheet(seeded, "clients", str(FIX / "clients_sample.xlsx"), commit=True)
    assert r.created == 1 and r.ok
    assert seeded.query(Client).filter_by(code="SWA-2025-CLT-002").one()


def test_import_inquiries_creates_and_links_client(seeded):
    r = import_sheet(seeded, "inquiries", str(FIX / "inquiries_sample.xlsx"), commit=True)
    assert r.created == 1 and r.ok
    inq = seeded.query(Inquiry).filter_by(reference_id="SWA-2025-INQ-002").one()
    assert inq.converted_client_id is not None


def test_import_agreements_creates(seeded):
    r = import_sheet(seeded, "agreements", str(FIX / "agreements_sample.xlsx"), commit=True)
    assert r.created == 1 and r.ok
    assert seeded.query(ServiceAgreement).filter_by(reference_id="SWA-2025-SA-012").one()


def test_import_tokens_creates(seeded):
    r = import_sheet(seeded, "tokens", str(FIX / "tokens_sample.xlsx"), commit=True)
    assert r.created == 1 and r.ok
    tok = seeded.query(Token).filter_by(reference_id="SWA-2025-TKN-001").one()
    assert tok.token_type == "Query"


def test_import_document_references_creates(seeded):
    r = import_sheet(
        seeded, "document_references", str(FIX / "document_references_sample.xlsx"), commit=True
    )
    assert r.created == 1 and r.ok
    doc = seeded.query(DocumentReference).filter_by(reference_id="SWA-2025-DRN-001").one()
    assert doc.project_id is not None


def test_import_projects_creates(seeded):
    r = import_sheet(seeded, "projects", str(FIX / "projects_sample.xlsx"), commit=True)
    assert r.created == 1 and r.ok
    assert seeded.query(Project).filter_by(code="SWA-2025-PRJ-066").one()


def test_import_time_logs_creates(seeded):
    r = import_sheet(seeded, "time_logs", str(FIX / "time_logs_sample.xlsx"), commit=True)
    assert r.created == 1 and r.ok
    assert seeded.query(TimeEntry).count() == 1


def test_import_sustainability_creates(seeded):
    r = import_sheet(
        seeded, "sustainability", str(FIX / "sustainability_sample.xlsx"), commit=True
    )
    assert r.created == 1 and r.ok
    m = seeded.query(SustainabilityMetric).filter_by(reference_id="SWA-2025-PRJ-065").one()
    assert m.energy_saved_kwh is not None


# --------------------------------------------------------------------------- #
# Dry-run, idempotency, error reporting
# --------------------------------------------------------------------------- #
def test_dry_run_does_not_persist(seeded):
    r = import_sheet(seeded, "tokens", str(FIX / "tokens_sample.xlsx"), commit=False)
    assert r.created == 1
    assert seeded.query(Token).filter_by(reference_id="SWA-2025-TKN-001").first() is None


def test_import_is_idempotent(seeded):
    import_sheet(seeded, "tokens", str(FIX / "tokens_sample.xlsx"), commit=True)
    r2 = import_sheet(seeded, "tokens", str(FIX / "tokens_sample.xlsx"), commit=True)
    assert r2.updated == 1 and r2.created == 0
    assert seeded.query(Token).filter_by(reference_id="SWA-2025-TKN-001").count() == 1


def test_missing_fk_reports_row_error(seeded, tmp_path):
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Columns", "Sr. No.", "Date", "Token ID", "Agreement ID", "Token Type",
               "Description", "Token Status", "Tokens Used", "Swa Employee Name/Team Leader",
               "Project Owner", "Client Employee Name"])
    ws.append(["", 1, "2025-10-03 00:00:00", "SWA-2025-TKN-999", "SWA-2025-SA-000",
               "Query", "desc", "In Progress", "1", "Mihir", "", "Akash"])
    bad = tmp_path / "bad_tokens.xlsx"
    wb.save(bad)
    r = import_sheet(seeded, "tokens", str(bad), commit=True)
    assert r.created == 0
    assert r.errors and r.errors[0]["row"] == 2


# --------------------------------------------------------------------------- #
# CLI smoke test (isolated SQLite)
# --------------------------------------------------------------------------- #
def test_cli_tokens_dry_run(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'cli.db'}"
    eng = create_engine(db_url, future=True)
    from src.backend.db.base import Base

    Base.metadata.create_all(eng)
    make_session = sessionmaker(bind=eng)
    with make_session() as s:
        c = Client(code="SWA-2025-CLT-001", name="Acme Corp", primary_email="a@b.com")
        s.add(c)
        s.flush()
        s.add(
            ServiceAgreement(
                reference_id="SWA-2025-SA-011",
                client_id=c.id,
                service_name="X",
                start_date=date.today(),
            )
        )
        s.commit()

    env = {**os.environ, "DATABASE_URL": db_url, "PYTHONPATH": str(REPO)}
    proc = subprocess.run(
        [sys.executable, "scripts/import_excel.py", "tokens",
         str(FIX / "tokens_sample.xlsx"), "--dry-run"],
        capture_output=True, text=True, env=env, cwd=str(REPO),
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["ok"] is True
    assert data["created"] == 1
