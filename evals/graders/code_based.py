"""
evals/graders/code_based.py — deterministic graders for wave-43 evals.

Each grader function is called by the harness (evals/harness/test_evals.py) after the
agent_steps have executed against a live FastAPI ASGI app + Postgres test DB (same
stack as tests/conftest.py). Graders assert on environmental state — DB rows, API
return payloads, Decimal arithmetic — never on UI text or "looks right".

A grader returns (passed: bool, evidence: str).

ctx contract (set by the harness, matching each task's *.task.yaml):
  - step responses are stored as ctx["stepN"]["response_body"] (raw JSON) or, where the
    grader only needs an id, ctx["stepN"]["<thing>_id"].
  - grader_001 reads ctx["step2"]["response_body"]["candidates"] and
    ctx["step3"]["response_body"] (client_id/project_id).
  - grader_002 reads ctx["step1"]["client_id"], ctx["step2"]["inquiry_id"],
    ctx["step3"]["response_body"]["project_id"], ctx["step4"]["agreement_id"],
    ctx["step5"]["token_id"], ctx["step6"]["docref_id"].
  - grader_003 reads ctx["step2"]["project_id"] and the *_status ints.
  - grader_004 reads ctx["step2"]["project_id"], ctx["step5"]["timesheet"],
    ctx["step6"]["invoice"].
  - grader_005 reads ctx["step3"]["invoice_id"] (string uuid).
"""
from __future__ import annotations

import re
import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

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
_YEAR_RE = re.compile(r"^SWA-(\d{4})-([A-Z]+)-(\d{3})$")


def _seq(ref: str) -> int:
    """Extract the 3-digit sequence number from a SWA ref."""
    m = _YEAR_RE.match(ref)
    return int(m.group(3)) if m else -1


def _year(ref: str) -> int:
    m = _YEAR_RE.match(ref)
    return int(m.group(1)) if m else -1


def _resp(ctx: dict, step: str) -> dict:
    """Get the full JSON response body for a step from ctx."""
    entry = ctx.get(step, {})
    return entry.get("response", entry.get("response_body", {}))


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
    """Verification:
      - inquiry.status == "Converted"
      - inquiry.converted_client_id == step2 candidates[0].id (reused, not new)
      - inquiry.converted_project_id != nil
      - client.code matches /^SWA-\\d{4}-CLT-\\d{3}$/
      - project.code == "APC-001"
      - client was reused (id == candidates[0].id), not newly created
    """
    ev = []
    try:
        inquiry_id = ctx["step1"]["inquiry_id"]
        inquiry = db.query(Inquiry).filter(Inquiry.id == uuid.UUID(inquiry_id)).one()
        _assert(inquiry.status == "Converted",
                f"inquiry.status == 'Converted' (got {inquiry.status})", ev)
        _assert(inquiry.converted_project_id is not None,
                "inquiry.converted_project_id is set", ev)

        # step2 response (300) contains candidates under "detail"
        step2_resp = _resp(ctx, "step2")
        candidates = step2_resp.get("candidates", []) if isinstance(step2_resp, dict) else []
        _assert(len(candidates) >= 1,
                f"step2 returned >=1 candidate (got {len(candidates)})", ev)
        picked_id = candidates[0]["id"]

        _assert(str(inquiry.converted_client_id) == str(picked_id),
                "inquiry.converted_client_id == picked candidate", ev)

        # step3 response has client_id + project_id
        step3_resp = _resp(ctx, "step3")
        client_id = step3_resp["client_id"]
        client = db.query(Client).filter(Client.id == uuid.UUID(client_id)).one()
        # In the ambiguous-REUSE branch (this task) the client already exists and keeps
        # its own code; we assert it was REUSED (id matches the picked candidate), not
        # that its code is SWA-format. The SWA-{year}-CLT- format only applies to the
        # new-client creation branch, which a different scenario would cover.
        _assert(str(client.id) == str(picked_id),
                "client was reused (not newly created) — matches candidates[0].id", ev)

        proj = db.query(Project).filter(
            Project.id == uuid.UUID(step3_resp["project_id"])
        ).one()
        _assert(proj.code == "APC-001", f"project.code == 'APC-001' (got {proj.code})", ev)
        _assert(str(proj.client_id) == str(client_id),
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
    """Verification:
      - all reference_ids match /^SWA-\\d{4}-[A-Z]+-\\d{3}$/
      - sequences monotonic across the chain (INQ < SA < TKN < DBR)
      - FK wiring: agreement.client_id, token.agreement_id, docref.token_id, docref.project_id
    """
    ev = []
    try:
        inq_id = ctx["step2"]["inquiry_id"]
        inq = db.query(Inquiry).filter(Inquiry.id == uuid.UUID(inq_id)).one()
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

        y = _year(inq.reference_id)
        seqs = [_seq(inq.reference_id), _seq(ag.reference_id),
                _seq(tok.reference_id), _seq(dr.reference_id)]
        _assert(all(_year(r) == y for r in
                    [inq.reference_id, ag.reference_id, tok.reference_id, dr.reference_id]),
                "all IDs share the same year", ev)
        _assert(seqs == sorted(seqs), f"sequences monotonic: {seqs}", ev)

        _assert(str(ag.client_id) == str(ctx["step1"]["client_id"]),
                "agreement.client_id links to client", ev)
        _assert(str(ag.inquiry_id) == str(inq_id),
                "agreement.inquiry_id links to inquiry", ev)
        _assert(str(tok.agreement_id) == str(ctx["step4"]["agreement_id"]),
                "token.agreement_id links to agreement", ev)
        step3_resp = _resp(ctx, "step3")
        _assert(str(dr.token_id) == str(ctx["step5"]["token_id"]),
                "docref.token_id links to token", ev)
        _assert(str(dr.project_id) == str(step3_resp["project_id"]),
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
    """Verification:
      - step3.status == 200   (viewer read allowed)
      - step4.status == 403   (viewer create client forbidden — exact)
      - step5.status == 403   (viewer project update forbidden — exact)
      - DB: no client with code "HACK-001"
      - DB: project.name unchanged ("RBAC Project")
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
    """Verification (the invoice is generated through the live API, exercising the real
    client workflow):
      - timesheet.total_hours == Decimal("8.00")
      - timesheet.billable_hours == Decimal("7.00")
      - timesheet.status == "draft"
      - exactly 2 time entries for the project (not soft-deleted)
      - the invoice generated from those time entries totals 41300.00 (35000 + 18% GST)
        and its money fields stay Decimal(18,2) with subtotal + gst_amount == total
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
        _assert(
            sum(Decimal(str(e.hours)) for e in entries) == Decimal("8.00"),
            f"sum of entry hours == 8.00 (got {sum(Decimal(str(e.hours)) for e in entries)})",
            ev,
        )

        inv = ctx["step6"]["invoice"]
        # 7 billable hours * 5000 = 35000; 18% GST = 6300; total = 41300
        _assert(Decimal(str(inv["total"])) == Decimal("41300.00"),
                f"invoice total == 41300.00 (got {inv['total']})", ev)
        _assert(Decimal(str(inv["gst_amount"])) == Decimal("6300.00"),
                f"invoice gst_amount == 6300.00 (got {inv['gst_amount']})", ev)
        _assert(Decimal(str(inv["subtotal"])) == Decimal("35000.00"),
                f"invoice subtotal == 35000.00 (got {inv['subtotal']})", ev)
        _assert(
            Decimal(str(inv["subtotal"])) + Decimal(str(inv["gst_amount"]))
            == Decimal(str(inv["total"])),
            "invoice subtotal + gst_amount == total (no rounding gap)", ev,
        )
        # Money stays Decimal on the model layer (anti-pattern guard: no silent float).
        db_inv = db.query(Invoice).filter(Invoice.id == uuid.UUID(inv["id"])).one()
        _assert(isinstance(db_inv.subtotal, Decimal),
                f"DB invoice.subtotal is Decimal (got {type(db_inv.subtotal).__name__})", ev)

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
    """Verification (the DB-layer Decimal(18,2) contract is authoritative; the API
    serializes Decimal as a JSON number, so the runtime invariant is numeric equality
    plus the model-layer type being Decimal to guard against silent float drift):
      - invoice.subtotal == 2950.00
      - invoice.gst_amount == 531.00
      - invoice.total == 3481.00
      - subtotal + gst_amount == total  (no rounding gap)
      - DB money fields are Decimal, not float
      - per-line amounts: 200.00, 750.00, 2000.00
    """
    ev = []
    try:
        inv_id = ctx["step3"]["invoice_id"]
        inv = db.query(Invoice).filter(Invoice.id == uuid.UUID(inv_id)).one()
        _ = inv.items  # trigger load

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

        # Money must stay Decimal on the model layer — anti-pattern guard #3.
        for fid in ("subtotal", "total", "gst_amount", "gst_percent", "tax_amount"):
            _assert(isinstance(getattr(inv, fid), Decimal),
                    f"DB {fid} is Decimal not float (got {type(getattr(inv, fid)).__name__})", ev)

        # Check item-level amounts
        amounts = sorted(Decimal(str(i.amount)) for i in inv.items)
        _assert(amounts == [Decimal("200.00"), Decimal("750.00"), Decimal("2000.00")],
                f"item amounts == [200, 750, 2000] (got {amounts})", ev)

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
