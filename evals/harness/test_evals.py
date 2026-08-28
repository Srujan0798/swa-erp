"""Wave-43 code-based evals — runnable pytest harness.

Each task is executed against the *live* FastAPI app (same ASGI stack the app ships
with) over a real Postgres test DB. Steps are driven through the real HTTP API exactly
as a client would; then the deterministic grader in evals/graders/code_based.py judges
the resulting environmental state (DB rows + API payloads).

Run:
    pytest evals/harness/ -q

This produces real pass/fail (pytest exit code) AND writes measured pass@k / pass^k
to evals/outcomes/pass@k.json plus per-trial transcripts to evals/transcripts/.

NOTE: the evals.yml CI workflow is intentionally non-blocking (continue-on-error).
These tests are the honest gate; they are NOT wired as a merge blocker.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from src.backend.core.roles import Role
from src.backend.schemas.user import UserCreate
from src.backend.services.user_service import create_user_service
from evals.graders.code_based import get_grader

HERE = Path(__file__).resolve().parent
OUTCOMES = HERE.parent / "outcomes" / "pass@k.json"
TRANSCRIPTS = HERE.parent / "transcripts"

DEFAULT_TRIALS = 3

# registry: task_id -> grader name (must match evals/graders/code_based.py GRADERS)
TASK_GRADERS = {
    "001-inquiry-to-client-conversion": "001_inquiry_conversion",
    "002-agreement-token-docref-chain": "002_id_chain",
    "003-rbac-enforcement": "003_rbac",
    "004-time-log-to-dashboard": "004_time_aggregation",
    "005-invoice-gst-correctness": "005_gst",
}


def _record(task_id: str, grader_name: str, results: list[dict]) -> None:
    """Write measured pass@k / pass^k to the outcomes JSON (per task)."""
    OUTCOMES.parent.mkdir(parents=True, exist_ok=True)
    data: dict = {}
    if OUTCOMES.exists():
        try:
            data = json.loads(OUTCOMES.read_text())
        except Exception:
            data = {}
    n = len(results)
    passed = sum(1 for r in results if r["passed"])
    data[task_id] = {
        "trials": n,
        "passed": passed,
        "pass@k": round(passed / n, 4) if n else 0.0,
        "pass^k": round(passed / n, 4) if n else 0.0,  # k-shot consistency
        "grader": grader_name,
        "results": results,
    }
    OUTCOMES.write_text(json.dumps(data, indent=2))


async def _as(client, token, method, url, **kw):
    """Issue a request with the bearer token; returns (status, json_or_text)."""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    resp = await getattr(client, method)(url, headers=headers, **kw)
    try:
        body = resp.json()
    except Exception:
        body = resp.text
    return resp.status_code, body


async def _seed_roles(db: Session, client):
    """Create one user per role, log them in, return (created, login).

    Called at the top of every trial AFTER the DB reset, so each trial is fully
    independent.
    """
    created = {}
    for role in ("admin", "pm", "designer", "auditor", "viewer"):
        email = f"{role}@eval.example.com"
        u = create_user_service(
            db,
            UserCreate(email=email, name=role.title(), password="EvalPass#123", role=Role(role)),
            actor_id=uuid.UUID(int=0),
        )
        created[role] = {"id": str(u.id), "email": email}
    db.commit()

    async def _login(role: str) -> str:
        resp = await client.post(
            "/api/auth/login",
            json={"email": created[role]["email"], "password": "EvalPass#123"},
        )
        assert resp.status_code == 200, f"login {role} -> {resp.status_code}: {resp.text}"
        return resp.json()["access_token"]

    return created, _login


async def _seed_two_clients_named(db: Session, name: str) -> list[str]:
    """Task 001 needs two existing clients sharing a name to trigger the 300 branch."""
    from src.backend.db.repositories.client_repo import create as create_client

    ids = []
    for _ in range(2):
        c = create_client(
            db,
            name=name,
            code=f"SEED-{uuid.uuid4().hex[:6].upper()}",
            primary_email=f"seed+{uuid.uuid4().hex[:6]}@swa.internal",
        )
        ids.append(str(c.id))
    db.commit()
    return ids


# ---------------------------------------------------------------------------
# Task 001 — Inquiry -> Client conversion (ambiguous-match branch)
# ---------------------------------------------------------------------------

async def trial_001(client, db: Session, reset_db) -> dict:
    reset_db()
    _, login = await _seed_roles(db, client)
    pm_token = await login("pm")

    await _seed_two_clients_named(db, "Ambiguous Test Client")

    ctx: dict = {}
    s, b = await _as(client, pm_token, "post", "/api/inquiries", json={
        "inquiry_date": "2026-08-28",
        "client_name": "Ambiguous Test Client",
        "requirement_summary": "Eval 001 — ambiguous client match",
    })
    assert s == 201, f"step1 create inquiry -> {s}: {b}"
    ctx["step1"] = {"inquiry_id": b["id"]}
    inquiry_id = b["id"]

    s, b = await _as(client, pm_token, "post", f"/api/inquiries/{inquiry_id}/convert", json={
        "project_name": "Ambiguous Project",
        "project_code": "APC-001",
    })
    assert s == 300, f"step2 ambiguous -> {s}: {b}"
    # FastAPI wraps HTTPException detail under "detail"; graders read response_body.candidates
    step2_body = b.get("detail", b) if isinstance(b, dict) else b
    ctx["step2"] = {"response_body": step2_body}
    candidates = step2_body.get("candidates") or []
    assert candidates, "step2 error body must carry candidates"

    s, b = await _as(client, pm_token, "post", f"/api/inquiries/{inquiry_id}/convert", json={
        "project_name": "Ambiguous Project",
        "project_code": "APC-001",
        "client_id": candidates[0]["id"],
    })
    assert s == 200, f"step3 convert -> {s}: {b}"
    ctx["step3"] = {"response_body": b}

    grader = get_grader("001_inquiry_conversion")
    passed, evidence = grader(ctx=ctx, db=db)
    return {"passed": passed, "evidence": evidence, "ctx": ctx}


# ---------------------------------------------------------------------------
# Task 002 — Agreement -> Token -> DocRef ID chain
# ---------------------------------------------------------------------------

async def trial_002(client, db: Session, reset_db) -> dict:
    reset_db()
    _, login = await _seed_roles(db, client)
    pm_token = await login("pm")

    ctx: dict = {}
    s, b = await _as(client, pm_token, "post", "/api/clients", json={
        "name": "Chain Client", "code": "CHN-001", "primary_email": "chain@test.com",
    })
    assert s == 201, f"002 step1 client -> {s}: {b}"
    ctx["step1"] = {"client_id": b["id"]}

    s, b = await _as(client, pm_token, "post", "/api/inquiries", json={
        "inquiry_date": "2026-08-28", "client_name": "Chain Client",
        "requirement_summary": "Eval 002 — ID chain",
    })
    assert s == 201, f"002 step2 inquiry -> {s}: {b}"
    inquiry_id = b["id"]
    ctx["step2"] = {"inquiry_id": inquiry_id}

    s, b = await _as(client, pm_token, "post", f"/api/inquiries/{inquiry_id}/convert", json={
        "project_name": "Chain Project", "project_code": "CHN-PRJ-001",
        "client_id": ctx["step1"]["client_id"],
    })
    assert s == 200, f"002 step3 convert -> {s}: {b}"
    ctx["step3"] = {"response_body": b, "project_id": b["project_id"]}

    s, b = await _as(client, pm_token, "post", "/api/service-agreements", json={
        "client_id": ctx["step1"]["client_id"], "inquiry_id": inquiry_id,
        "service_name": "Annual Maintenance Contract",
        "start_date": "2026-01-01", "end_date": "2026-12-31", "total_tokens": 100,
    })
    assert s == 201, f"002 step4 agreement -> {s}: {b}"
    ctx["step4"] = {"agreement_id": b["id"]}

    s, b = await _as(client, pm_token, "post", "/api/tokens", json={
        "agreement_id": ctx["step4"]["agreement_id"], "token_date": "2026-08-28",
        "token_type": "SA", "description": "Eval token", "tokens_used": 1,
        "project_id": ctx["step3"]["project_id"],
    })
    assert s == 201, f"002 step5 token -> {s}: {b}"
    ctx["step5"] = {"token_id": b["id"]}

    s, b = await _as(client, pm_token, "post", "/api/document-references", json={
        "project_id": ctx["step3"]["project_id"], "token_id": ctx["step5"]["token_id"],
        "document_type": "DBR", "doc_date": "2026-08-28", "description": "Eval docref",
    })
    assert s == 201, f"002 step6 docref -> {s}: {b}"
    ctx["step6"] = {"docref_id": b["id"]}

    grader = get_grader("002_id_chain")
    passed, evidence = grader(ctx=ctx, db=db)
    return {"passed": passed, "evidence": evidence, "ctx": ctx}


# ---------------------------------------------------------------------------
# Task 003 — RBAC enforcement (Viewer cannot mutate)
# ---------------------------------------------------------------------------

async def trial_003(client, db: Session, reset_db) -> dict:
    reset_db()
    _, login = await _seed_roles(db, client)
    admin_token = await login("admin")
    viewer_token = await login("viewer")

    s, b = await _as(client, admin_token, "post", "/api/clients", json={
        "name": "RBAC Client", "code": "RBAC-CLT", "primary_email": "rbac@test.com",
    })
    assert s == 201, f"003 seed client -> {s}: {b}"
    client_id = b["id"]
    s, b = await _as(client, admin_token, "post", "/api/projects", json={
        "client_id": client_id, "name": "RBAC Project",
        "code": f"RBAC-{uuid.uuid4().hex[:6].upper()}", "status": "Lead",
    })
    assert s == 201, f"003 seed project -> {s}: {b}"
    project_id = b["id"]

    ctx: dict = {"step2": {"project_id": project_id}}

    s, _ = await _as(client, viewer_token, "get", "/api/projects")
    ctx["step3_status"] = s

    s, _ = await _as(client, viewer_token, "post", "/api/clients", json={
        "name": "HACK Client", "code": "HACK-001", "primary_email": "hack@test.com",
    })
    ctx["step4_status"] = s

    s, _ = await _as(client, viewer_token, "patch", f"/api/projects/{project_id}", json={
        "name": "HACKED NAME",
    })
    ctx["step5_status"] = s

    grader = get_grader("003_rbac")
    passed, evidence = grader(ctx=ctx, db=db)
    return {"passed": passed, "evidence": evidence, "ctx": ctx}


# ---------------------------------------------------------------------------
# Task 004 — Time log -> dashboard aggregation (invoice from time)
# ---------------------------------------------------------------------------

async def trial_004(client, db: Session, reset_db) -> dict:
    reset_db()
    _, login = await _seed_roles(db, client)
    pm_token = await login("pm")

    ctx: dict = {}
    s, b = await _as(client, pm_token, "post", "/api/clients", json={
        "name": "Time Client", "code": f"TM-{uuid.uuid4().hex[:6].upper()}",
        "primary_email": "time@test.com",
    })
    assert s == 201, f"004 client -> {s}: {b}"
    client_id = b["id"]
    s, b = await _as(client, pm_token, "post", "/api/projects", json={
        "client_id": client_id, "name": "Time Project",
        "code": f"TM-{uuid.uuid4().hex[:6].upper()}", "status": "Awarded",
    })
    assert s == 201, f"004 project -> {s}: {b}"
    project_id = b["id"]
    ctx["step2"] = {"project_id": project_id}

    for i, (hours, billable) in enumerate([(7, True), (1, False)], start=1):
        s, b = await _as(client, pm_token, "post", "/api/time-entries", json={
            "project_id": project_id, "date": "2026-08-25",
            "hours": hours, "description": f"Entry {i}", "is_billable": billable,
        })
        assert s == 201, f"004 entry {i} -> {s}: {b}"

    s, b = await _as(client, pm_token, "post", "/api/timesheets/generate",
                     params={"week_start": "2026-08-24"})
    assert s == 200, f"004 timesheet -> {s}: {b}"
    ctx["step5"] = {"timesheet": b}

    s, b = await _as(client, pm_token, "post",
                     f"/api/projects/{project_id}/invoices/generate-from-time", json={
                         "start_date": "2026-08-24", "end_date": "2026-08-30",
                     })
    assert s == 201, f"004 invoice -> {s}: {b}"
    ctx["step6"] = {"invoice": b}

    grader = get_grader("004_time_aggregation")
    passed, evidence = grader(ctx=ctx, db=db)
    return {"passed": passed, "evidence": evidence, "ctx": ctx}


# ---------------------------------------------------------------------------
# Task 005 — Invoice GST correctness (Decimal(18,2))
# ---------------------------------------------------------------------------

async def trial_005(client, db: Session, reset_db) -> dict:
    reset_db()
    _, login = await _seed_roles(db, client)
    pm_token = await login("pm")

    ctx: dict = {}
    s, b = await _as(client, pm_token, "post", "/api/clients", json={
        "name": "GST Client", "code": f"GST-{uuid.uuid4().hex[:6].upper()}",
        "primary_email": "gst@test.com",
    })
    assert s == 201, f"005 client -> {s}: {b}"
    client_id = b["id"]
    s, b = await _as(client, pm_token, "post", "/api/projects", json={
        "client_id": client_id, "name": "GST Project",
        "code": f"GST-{uuid.uuid4().hex[:6].upper()}", "status": "Awarded",
    })
    assert s == 201, f"005 project -> {s}: {b}"
    project_id = b["id"]

    # items: 2000 + 750 + 200 = 2950 subtotal; 18% GST = 531; total = 3481
    s, b = await _as(client, pm_token, "post",
                     f"/api/projects/{project_id}/invoices", json={
                         "tax_rate": "18.00",
                         "items": [
                             {"description": "Design", "quantity": "1",
                              "rate": "2000.00", "amount": "2000.00"},
                             {"description": "Review", "quantity": "1",
                              "rate": "750.00", "amount": "750.00"},
                             {"description": "Doc", "quantity": "1",
                              "rate": "200.00", "amount": "200.00"},
                         ],
                     })
    assert s == 201, f"005 invoice -> {s}: {b}"
    ctx["step3"] = {"invoice_id": b["id"]}  # string id; grader wraps with uuid.UUID()

    grader = get_grader("005_gst")
    passed, evidence = grader(ctx=ctx, db=db)
    return {"passed": passed, "evidence": evidence, "ctx": ctx}


TRIALS = {
    "001-inquiry-to-client-conversion": trial_001,
    "002-agreement-token-docref-chain": trial_002,
    "003-rbac-enforcement": trial_003,
    "004-time-log-to-dashboard": trial_004,
    "005-invoice-gst-correctness": trial_005,
}


@pytest.mark.parametrize("task_id", list(TRIALS.keys()))
async def test_eval_task(client, db_session, reset_db, task_id):
    """Run one task for DEFAULT_TRIALS independent trials; record + assert.

    A real pytest FAIL here is the honest signal that the system does not do the job.
    pass@k / pass^k are written to evals/outcomes/pass@k.json for the baseline report.
    """
    trial_fn = TRIALS[task_id]
    grader_name = TASK_GRADERS[task_id]
    results = []
    for trial in range(1, DEFAULT_TRIALS + 1):
        res = await trial_fn(client, db_session, reset_db)
        results.append({
            "trial": trial,
            "passed": bool(res["passed"]),
            "evidence": res.get("evidence", ""),
        })
        TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
        (TRANSCRIPTS / f"{task_id}.trial-{trial}.json").write_text(
            json.dumps(res, indent=2, default=str)
        )

    _record(task_id, grader_name, results)

    n = len(results)
    passed = sum(1 for r in results if r["passed"])
    assert passed == n, (
        f"{task_id}: {passed}/{n} trials passed.\n"
        + "\n---\n".join(r["evidence"] for r in results if not r["passed"])
    )
