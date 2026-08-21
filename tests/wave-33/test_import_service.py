"""Wave 33 — import_service coverage (REDO).

Complements tests/wave-13 (which covers happy-path sheet imports on SQLite)
by exercising, against the main Postgres-backed conftest: stub client/project
creation, malformed-input error reporting, idempotency, sheet-reader fallbacks,
and unknown-sheet/fatal-path handling.
"""
from __future__ import annotations

from datetime import date

import openpyxl
import pytest
from sqlalchemy import select

from src.backend.models import (
    Client,
    DocumentReference,
    Inquiry,
    Project,
    ServiceAgreement,
    SustainabilityMetric,
    TimeEntry,
    Token,
    User,
)
from src.backend.services.import_service import (
    ImportResult,
    _looks_like_swa_id,
    _parse_bool,
    _parse_date,
    _parse_decimal,
    _parse_int,
    _record_get,
    import_sheet,
)


@pytest.fixture
def seeded(db_session):
    client = Client(
        code="SWA-2025-CLT-001",
        name="Acme Corp",
        primary_email="acme@example.com",
    )
    db_session.add(client)
    db_session.flush()
    db_session.add(
        Inquiry(
            reference_id="SWA-2025-INQ-001",
            inquiry_date=date.today(),
            client_name="Acme Corp",
            status="New",
        )
    )
    db_session.add(
        ServiceAgreement(
            reference_id="SWA-2025-SA-011",
            client_id=client.id,
            service_name="INSUDESIGN",
            start_date=date.today(),
        )
    )
    db_session.add(Project(code="SWA-2025-PRJ-065", client_id=client.id, name="Green Tower"))
    db_session.commit()
    return db_session


def _sheet(tmp_path, headers, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(headers)
    for r in rows:
        ws.append(r)
    path = tmp_path / "input.xlsx"
    wb.save(path)
    return str(path)


# --------------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------------- #
def test_parse_date_variants():
    assert _parse_date(None) is None
    assert _parse_date("") is None
    assert _parse_date("N/A") is None
    assert _parse_date("2026-01-15") == date(2026, 1, 15)
    assert _parse_date("15/01/2026") == date(2026, 1, 15)
    assert _parse_date("15-01-2026") == date(2026, 1, 15)
    with pytest.raises(ValueError, match="unrecognized date"):
        _parse_date("not a date")


def test_parse_decimal_variants():
    assert _parse_decimal(None) is None
    assert _parse_decimal("") is None
    assert _parse_decimal("N/A") is None
    assert _parse_decimal("1,234.50") == 1234.50
    with pytest.raises(ValueError, match="not a number"):
        _parse_decimal("abc")


def test_parse_int_variants():
    assert _parse_int(None) is None
    assert _parse_int("") is None
    assert _parse_int("1,000") == 1000
    assert _parse_int("42.9") == 42
    with pytest.raises(ValueError, match="not an integer"):
        _parse_int("abc")


def test_parse_bool_variants():
    assert _parse_bool(None) is None
    assert _parse_bool("") is None
    assert _parse_bool("yes") is True
    assert _parse_bool("true") is True
    assert _parse_bool("no") is False
    assert _parse_bool("0") is False
    with pytest.raises(ValueError, match="not a boolean"):
        _parse_bool("maybe")


def test_looks_like_swa_id():
    assert _looks_like_swa_id("SWA-2025-PRJ-001") is True
    assert _looks_like_swa_id("PRJ-2025-001") is True
    assert _looks_like_swa_id("plain text") is False
    assert _looks_like_swa_id(None) is False
    assert _looks_like_swa_id("") is False


def test_record_get_case_insensitive_fallback():
    record = {"Client ID": "SWA-2025-CLT-001", "Client Name": "Acme", "Blank": ""}
    assert _record_get(record, "client id") == "SWA-2025-CLT-001"
    assert _record_get(record, "CLIENT NAME") == "Acme"
    assert _record_get(record, "Missing", "Also Missing") is None
    assert _record_get(record, "Blank") is None


def test_import_result_to_dict_and_ok():
    r = ImportResult(sheet_type="clients", total_rows=1, created=1)
    assert r.ok is True
    d = r.to_dict()
    assert d["sheet_type"] == "clients"
    assert d["ok"] is True
    r.add_error(2, "boom")
    assert r.ok is False
    assert r.to_dict()["errors"] == [{"row": 2, "message": "boom"}]


# --------------------------------------------------------------------------- #
# Stub creation (allow_stubs)
# --------------------------------------------------------------------------- #
def test_ensure_client_stub_created_when_stubs_allowed(seeded, tmp_path):
    path = _sheet(
        tmp_path,
        ["Agreement ID", "Client ID", "Client Name", "Service Name", "Start Date"],
        [["SWA-2025-SA-099", None, "New Client Co", "CONSULT", "2026-01-01"]],
    )
    r = import_sheet(seeded, "agreements", path, commit=True, allow_stubs=True)
    assert r.ok, r.errors
    stub = seeded.scalar(
        select(Client).where(Client.code == "IMP-NEW-CLIENT-CO")
    )
    assert stub is not None
    assert seeded.scalar(
        select(ServiceAgreement).where(ServiceAgreement.reference_id == "SWA-2025-SA-099")
    )


def test_stub_creation_refused_when_stubs_disabled(seeded, tmp_path):
    path = _sheet(
        tmp_path,
        ["Agreement ID", "Client ID", "Client Name", "Service Name", "Start Date"],
        [["SWA-2025-SA-100", None, "Ghost Co", "CONSULT", "2026-01-01"]],
    )
    r = import_sheet(seeded, "agreements", path, commit=True, allow_stubs=False)
    assert r.created == 0
    assert r.errors and "client not found" in r.errors[0]["message"]


def test_ensure_project_stub_created_for_doc_ref(seeded, tmp_path):
    path = _sheet(
        tmp_path,
        ["Doc Ref No", "Associated Project ID", "Date", "Document Type", "Status"],
        [["SWA-2025-DRN-777", "SWA-2025-PRJ-999", "2026-01-01", "GAD", "Draft"]],
    )
    r = import_sheet(
        seeded, "document_references", path, commit=True, allow_stubs=True
    )
    assert r.ok, r.errors
    stub = seeded.scalar(select(Project).where(Project.code == "SWA-2025-PRJ-999"))
    assert stub is not None
    assert stub.client_id is not None
    doc = seeded.scalar(
        select(DocumentReference).where(DocumentReference.reference_id == "SWA-2025-DRN-777")
    )
    assert doc.project_id == stub.id


# --------------------------------------------------------------------------- #
# Malformed input / error reporting
# --------------------------------------------------------------------------- #
def test_missing_key_fields_report_row_errors(seeded, tmp_path):
    path = _sheet(
        tmp_path,
        ["Client ID", "Client Name", "Email"],
        [["SWA-2025-CLT-999", None, "x@y.com"], ["SWA-2025-CLT-998", "Fine", "z@w.com"]],
    )
    r = import_sheet(seeded, "clients", path, commit=True)
    assert r.created == 1
    messages = [e["message"] for e in r.errors]
    assert "missing Client Name" in messages


def test_bad_inquiry_date_reports_error(seeded, tmp_path):
    path = _sheet(
        tmp_path,
        ["Inquiry ID", "Inquiry Date", "Client Name"],
        [["SWA-2025-INQ-999", "garbage", "Acme Corp"]],
    )
    r = import_sheet(seeded, "inquiries", path, commit=True)
    assert r.created == 0
    assert r.errors and "unrecognized date" in r.errors[0]["message"]


def test_token_missing_agreement_reports_error(seeded, tmp_path):
    path = _sheet(
        tmp_path,
        ["Token ID", "Agreement ID", "Date", "Token Type"],
        [["SWA-2025-TKN-999", "SWA-2025-SA-NOPE", "2026-01-01", "Query"]],
    )
    r = import_sheet(seeded, "tokens", path, commit=True)
    assert r.created == 0
    assert r.errors and "not found" in r.errors[0]["message"]


def test_doc_ref_missing_project_reports_error(seeded, tmp_path):
    path = _sheet(
        tmp_path,
        ["Doc Ref No", "Date", "Document Type"],
        [["SWA-2025-DRN-600", "2026-01-01", "GAD"]],
    )
    r = import_sheet(seeded, "document_references", path, commit=True)
    assert r.created == 0
    assert r.errors and "not found" in r.errors[0]["message"]


def test_project_missing_client_reports_error(seeded, tmp_path):
    path = _sheet(
        tmp_path,
        ["Project ID", "Client ID", "Project Name"],
        [["SWA-2025-PRJ-888", "SWA-2025-CLT-NOPE", "Tower"]],
    )
    r = import_sheet(seeded, "projects", path, commit=True)
    assert r.created == 0
    assert r.errors and "not found" in r.errors[0]["message"]


def test_time_logs_unknown_ref_reports_error(seeded, tmp_path):
    path = _sheet(
        tmp_path,
        ["Reference ID", "Date", "Hours Logged", "Activity Type"],
        [["NOT-A-CODE", "2026-01-01", "2.5", "Design"]],
    )
    r = import_sheet(seeded, "time_logs", path, commit=True)
    assert r.created == 0
    assert r.errors and "not found" in r.errors[0]["message"]


def test_sustainability_green_string_falls_back_to_true(seeded, tmp_path):
    path = _sheet(
        tmp_path,
        ["Reference ID", "Date", "Compliant with Green Standards", "Notes"],
        [["SWA-2025-PRJ-065", "2026-01-01", "IGBC", "gold"]],
    )
    r = import_sheet(seeded, "sustainability", path, commit=True)
    assert r.ok, r.errors
    m = seeded.scalar(
        select(SustainabilityMetric).where(
            SustainabilityMetric.reference_id == "SWA-2025-PRJ-065"
        )
    )
    assert m.compliant_with_green_standards is True


# --------------------------------------------------------------------------- #
# Idempotency
# --------------------------------------------------------------------------- #
def test_document_reference_import_is_idempotent(seeded, tmp_path):
    path = _sheet(
        tmp_path,
        ["Doc Ref No", "Associated Project ID", "Date", "Document Type", "Status"],
        [["SWA-2025-DRN-500", "SWA-2025-PRJ-065", "2026-01-01", "GAD", "Draft"]],
    )
    r1 = import_sheet(seeded, "document_references", path, commit=True)
    assert r1.created == 1
    r2 = import_sheet(seeded, "document_references", path, commit=True)
    assert r2.updated == 1
    assert r2.created == 0
    assert seeded.scalar(
        select(DocumentReference).where(DocumentReference.reference_id == "SWA-2025-DRN-500")
    )


def test_time_logs_duplicate_row_skipped(seeded, tmp_path):
    path = _sheet(
        tmp_path,
        ["Reference ID", "Date", "Hours Logged", "Activity Type", "Employee Name"],
        [["SWA-2025-PRJ-065", "2026-01-01", "1.5", "Design", "Mihir"]],
    )
    r1 = import_sheet(seeded, "time_logs", path, commit=True)
    assert r1.created == 1
    r2 = import_sheet(seeded, "time_logs", path, commit=True)
    assert r2.skipped == 1
    assert r2.created == 0
    assert seeded.scalar(select(TimeEntry)) is not None


# --------------------------------------------------------------------------- #
# Sheet reader / dispatch edge cases
# --------------------------------------------------------------------------- #
def test_unknown_sheet_type_raises(seeded):
    with pytest.raises(ValueError, match="unknown sheet_type"):
        import_sheet(seeded, "nonsense", "whatever.xlsx")


def test_missing_file_reports_fatal_error(seeded, tmp_path):
    r = import_sheet(seeded, "clients", str(tmp_path / "missing.xlsx"), commit=True)
    assert r.created == 0
    assert r.errors and r.errors[0]["row"] == 0
    assert "Fatal" in r.errors[0]["message"]


def test_dry_run_does_not_commit(seeded, tmp_path):
    path = _sheet(
        tmp_path,
        ["Project ID", "Client ID", "Project Name"],
        [["SWA-2025-PRJ-700", "SWA-2025-CLT-001", "Dry Run Tower"]],
    )
    r = import_sheet(seeded, "projects", path, commit=False)
    assert r.created == 1
    assert seeded.scalar(select(Project).where(Project.code == "SWA-2025-PRJ-700")) is None


def test_clients_update_path(seeded, tmp_path):
    path = _sheet(
        tmp_path,
        ["Client ID", "Client Name", "Email", "Phone"],
        [["SWA-2025-CLT-001", "Acme Corp Renamed", "acme@example.com", "555-0100"]],
    )
    r = import_sheet(seeded, "clients", path, commit=True)
    assert r.updated == 1
    c = seeded.scalar(select(Client).where(Client.code == "SWA-2025-CLT-001"))
    assert c.name == "Acme Corp Renamed"
    assert c.primary_phone == "555-0100"