"""
evals/graders/code_based.py — deterministic graders for wave-43 evals.

Each grader function is called by evals/run_evals.py after the agent_steps have
executed against a live FastAPI ASGI app + Postgres test DB (same stack as
tests/conftest.py). Graders assert on environmental state — DB rows, API payloads,
Decimal arithmetic — never on UI text or "looks right".

A grader returns (passed: bool, evidence: str).
"""
from __future__ import annotations

import re
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from src.backend.core.config import settings
from src.backend.models.agreement import ServiceAgreement
from src.backend.models.client import Client
from src.backend.models.document_reference import DocumentReference
from src.backend.models.invoice import Invoice, InvoiceItem
from src.backend.models.inquiry import Inquiry
from src.backend.models.project import Project
from src.backend.models.time_tracking import TimeEntry, Timesheet
from src.backend.models.token import Token


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REF_RE = re.compile(r"^SWA-\d{4}-[A-Z]+-\d{3}$")
_YEAR_RE = re.compile(r"^SWA-(\d{4})-[A-Z]+-(\d{3})$")


def _seq(ref: str) -> int:
    """Extract the 3-digit sequence number from a SWA ref."""
    m = _YEAR_RE.match(ref)
    return int(m.group(2)) if m else -1


def _year(ref: str) -> int:
    m = _YEAR_RE.match(ref)
    return int(m.group(1)) if m else -1


def _assert(cond: bool, msg: str, evidence: list[str]) -> list[str]:
    """Append pass/fail line to evidence. Raises AssertionError if cond is False."""
    if cond:
        evidence.append(f"  PASS: {msg}")
    else:
        evidence.append(f"  FAIL: {msg}")
    assert cond, msg
    return evidence


# ---------------------------------------------------------------------------
# Task 001: Inquiry -> Client conversion (incl. ambiguous-match branch)
# ---------------------------------------------------------------------------

def grader_001_inquiry_conversion(
    *,
    ctx: dict,
    db: Session,
) -> tuple[bool, str]:
    """
    Verification:
      - inquiry.status == "Converted"
      - inquiry.converted_client_id == step2.candidates[0].id (the picked client)
      - inquiry.converted_project_id != nil
      - client.id == step2.candidates[0].id  (reused, NOT a new one)
      - project.code == "APC-001"
      - client.code matches /^SWA-\\d{4}-CLT-\\d{3}$/
    """
    ev = []
    try:
        inquiry_id = ctx["step1"]["inquiry_id"]
        inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).one()
        _assert(inquiry.status == "Converted",
                f"inquiry.status == 'Converted' (got {inquiry.status})", ev)
        _assert(
            str(inquiry.converted_client_id) == str(ctx["step2"]["candidates"][0]["id"]),
            "inquiry.converted_client_id == picked candidate", ev,
        )
        _assert(inquiry.converted_project_id is not None,
                "inquiry.converted_project_id is set", ev)

        client_id = ctx["step3"]["result"]["client_id"]
        client = db.query(Client).filter(Client.id == uuid.UUID(client_id)).one()
        _assert(bool(_REF_RE.match(client.code)),
                f"client.code matches {_REF_RE.pattern} (got {client.code})", ev)
        _assert(
            str(client.id) == str(ctx["step2"]["candidates"][0]["id"]),
            "client was reused (not newly created) — matches candidates[0].id", ev,
        )

        proj = db.query(Project).filter(
            Project.id == uuid.UUID(ctx["step3"]["result"]["project_id"])
        ).one()
        _assert(proj.code == "APC-001", f"project.code == 'APC-001' (got {proj.code})", ev)
        _assert(proj.client_id == uuid.UUID(client_id),
                "project.client_id links to the reused client", ev)

        return True, "\n".join(ev)

    except AssertionError:
        return False, "\n".join(ev)
    except Exception as e:
        return False, f"EXCEPTION: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Task 002: Agreement -> Token -> DocRef ID chain
# ---------------------------------------------------------------------------

def grader_002_id_chain(
    *,
    ctx: dict,
    db: Session,
) -> tuple[bool, str]:
    """
    Verification:
      - all reference_ids match /^SWA-\\d{4}-[A-Z]+-\\d{3}$/
      - sequences monotonic across the chain (INQ < SA < TKN < DBR)
      - FK wiring: agreement.client_id, token.agreement_id, docref.token_id, docref.project_id
    """
    ev = []
    try:
        inq = db.query(Inquiry).filter(
            Inquiry.id == uuid.UUID(ctx["step2"]["inquiry_id"])
        ).one()
        ag = db.query(ServiceAgreement).filter(
            ServiceAgreement.id == uuid.UUID(ctx["step4"]["agreement_id"])
        ).one()
        tok = db.query(Token).filter(
            Token.id == uuid.UUID(ctx["step5"]["token_id"])
        ).one()
        dr = db.query(DocumentReference).filter(
            DocumentReference.id == uuid.UUID(ctx["step6"]["docref_id"])
        ).one()

        for label, obj in [("inquiry", inq), ("agreement", ag), ("token", tok), ("docref", dr)]:
            _assert(bool(_REF_RE.match(obj.reference_id)),
                    f"{label}.reference_id matches format (got {obj.reference_id})", ev)

        # monotonic within the same year
        y = _year(inq.reference_id)
        seqs = [inq.reference_id, ag.reference_id, tok.reference_id, dr.reference_id]
        seq_nums = [_seq(r) for r in seqs]
        _assert(
            all(_year(r) == y for r in seqs),
            "all IDs share the same year", ev,
        )
        _assert(seq_nums == sorted(seq_nums),
                f"sequences monotonic: {seq_nums}", ev)

        # FK wiring
        _assert(str(ag.client_id) == ctx["step1"]["client_id"],
                "agreement.client_id links to client", ev)
        _assert(str(ag.inquiry_id) == ctx["step2"]["inquiry_id"],
                "agreement.inquiry_id links to inquiry", ev)
        _assert(str(tok.agreement_id) == ctx["step4"]["agreement_id"],
                "token.agreement_id links to agreement", ev)
        _assert(str(dr.token_id) == ctx["step5"]["token_id"],
                "docref.token_id links to token", ev)
        _assert(str(dr.project_id) == ctx["step3"]["project_id"],
                "docref.project_id links to project", ev)

        return True, "\n".join(ev)

    except AssertionError:
        return False, "\n".join(ev)
    except Exception as e:
        return False, f"EXCEPTION: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Task 003: RBAC enforcement
# ---------------------------------------------------------------------------

def grader_003_rbac(
    *,
    ctx: dict,
    db: Session,
) -> tuple[bool, str]:
    """
    Verification:
      - step3.status == 200   (viewer read allowed)
      - step4.status == 403   (viewer create client forbidden — exact)
      - step5.status == 403   (viewer project update forbidden — exact)
      - DB: no client with code "HACK-001"
      - DB: project.name unchanged
    """
    ev = []
    try:
        _assert(ctx["step3_status"] == 200,
                f"viewer read projects allowed (got {ctx['step3_status']})", ev)
        _assert(ctx["step4_status"] == 403,
                f"viewer create client -> 403 (got {ctx['step4_status']})", ev)
        _assert(ctx["step5_status"] == 403,
                f"viewer update project -> 403 (got {ctx['step5_status']})", ev)

        hack = db.query(Client).filter(Client.code == "HACK-001").first()
        _assert(hack is None, "no 'HACK-001' client created by viewer", ev)

        proj = db.query(Project).filter(
            Project.id == uuid.UUID(ctx["step2"]["project_id"])
        ).one()
        _assert(proj.name == "RBAC Project",
                f"project.name unchanged ('{proj.name}')", ev)

        return True, "\n".join(ev)

    except AssertionError:
        return False, "\n".join(ev)
    except Exception as e:
        return False, f"EXCEPTION: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Task 004: Time log -> dashboard aggregation
# ---------------------------------------------------------------------------

def grader_004_time_aggregation(
    *,
    ctx: dict,
    db: Session,
) -> tuple[bool, str]:
    """
    Verification:
      - timesheet.total_hours == Decimal("8.00")
      - timesheet.billable_hours == Decimal("7.00")
      - timesheet.status == "draft"
      - 2 time entries for the project
      - invoice from time entries totals 41300.00 (35000 + 18% GST)
    """
    ev = []
    try:
        ts = ctx["step5"]["timesheet"]
        _assert(Decimal(str(ts["total_hours"])) == Decimal("8.00"),
                f"timesheet.total_hours == 8.00 (got {ts['total_hours']})", ev)
        _assert(Decimal(str(ts["billable_hours"])) == Decimal("7.00"),
                f"timesheet.billable_hours == 7.00 (got {ts['billable_hours']})", ev)
        _assert(ts["status"] == "draft",
                f"timesheet.status == 'draft' (got {ts['status']})", ev)

        proj_id = uuid.UUID(ctx["step2"]["project_id"])
        entries = db.query(TimeEntry).filter(
            TimeEntry.project_id == proj_id,
            TimeEntry.deleted_at.is_(None),
        ).all()
        _assert(len(entries) == 2, f"2 time entries exist (got {len(entries)})", ev)

        # Verify the generate-from-time invoice
        from src.backend.services.invoice_service import generate_from_time_entries
        from src.backend.core.config import settings as _settings

        admin_user_id = ctx.get("admin_user_id")
        assert admin_user_id is not None, "ctx must include admin_user_id"
        # We call the service directly to validate the invoice arithmetic
        from datetime import date as dt
        inv = generate_from_time_entries(
            db,
            project_id=proj_id,
            user_id=admin_user_id,
            start_date=dt(2026, 8, 24),
            end_date=dt(2026, 8, 30),
        )
        # 7 billable hours * 5000 = 35000; 18% GST = 6300; total = 41300
        _assert(
            Decimal(str(inv["total"])) == Decimal("41300.00"),
            f"invoice total == 41300.00 (got {inv['total']})", ev,
        )
        _assert(
            Decimal(str(inv["gst_amount"])) == Decimal("6300.00"),
            f"invoice gst_amount == 6300.00 (got {inv['gst_amount']})", ev,
        )
        _assert(
            Decimal(str(inv["subtotal"])) == Decimal("35000.00"),
            f"invoice subtotal == 35000.00 (got {inv['subtotal']})", ev,
        )

        return True, "\n".join(ev)

    except AssertionError:
        return False, "\n".join(ev)
    except Exception as e:
        return False, f"EXCEPTION: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Task 005: Invoice GST correctness
# ---------------------------------------------------------------------------

def grader_005_gst(
    *,
    ctx: dict,
    db: Session,
) -> tuple[bool, str]:
    """
    Verification:
      - invoice.subtotal == 2950.00
      - invoice.gst_amount == 531.00
      - invoice.total == 3481.00
      - subtotal + gst_amount == total  (no rounding gap)
      - money fields are str, not float
      - per-line amounts: 2000.00, 750.00, 200.00
    """
    ev = []
    try:
        inv_id = ctx["step3"]["invoice_id"]
        inv = db.query(Invoice).filter(Invoice.id == inv_id).all()
        # reload with items via relationship
        inv = db.query(Invoice).filter(Invoice.id == inv_id).one()
        _ = inv.items  # eager load

        _assert(Decimal(str(inv.subtotal)) == Decimal("2950.00"),
                f"subtotal == 2950.00 (got {inv.subtotal})", ev)
        _assert(Decimal(str(inv.gst_percent)) == Decimal("18.00"),
                f"gst_percent == 18.00 (got {inv.gst_percent})", ev)
        _assert(Decimal(str(inv.gst_amount)) == Decimal("531.00"),
                f"gst_amount == 531.00 (got {inv.gst_amount})", ev)
        _assert(Decimal(str(inv.total)) == Decimal("3481.00"),
                f"total == 3481.00 (got {inv.total})", ev)
        _assert(
            Decimal(str(inv.subtotal)) + Decimal(str(inv.gst_amount)) == Decimal(str(inv.total)),
            "subtotal + gst_amount == total (no rounding gap)", ev,
        )

        # Check item-level amounts
        amounts = sorted(Decimal(str(i.amount)) for i in inv.items)
        _assert(amounts == [Decimal("200.00"), Decimal("750.00"), Decimal("2000.00")],
                f"item amounts == [200, 750, 2000] (got {amounts})", ev)

        # Verify money fields serialize as strings in the API response (Decimal -> str in Pydantic)
        # We check the raw JSON from the create response
        # The ctx stores the raw JSON dict from the POST
        inv_json = ctx["step3"]["response_body"]
        for fid in ("subtotal", "gst_amount", "total", "gst_percent", "tax_amount"):
            val = inv_json.get(fid)
            _assert(isinstance(val, str),
                    f"JSON {fid} is str not float (got {type(val).__name__}: {val})", ev)

        return True, "\n".join(ev)

    except AssertionError:
        return False, "\n".join(ev)
    except Exception as e:
        return False, f"EXCEPTION: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Registry — maps task grader names to functions
# ---------------------------------------------------------------------------

GRADERS = {
    "001_inquiry_conversion": grader_001_inquiry_conversion,
    "002_id_chain": grader_002_id_chain,
    "003_rbac": grader_003_rbac,
    "004_time_aggregation": grader_004_time_aggregation,
    "005_gst": grader_005_gst,
}


def get_grader(name: str):
    return GRADERS.get(name)
