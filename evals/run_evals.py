#!/usr/bin/env python3
"""
evals/run_evals.py — the eval runner.

Executes eval tasks defined in evals/tasks/*.task.yaml against the live FastAPI
ASGI app (using the same test stack as tests/conftest.py: ASGITransport + httpx
AsyncClient + SQLAlchemy session bound to Postgres).

For each task:
  1. Reset the DB to a clean state (fresh schema per trial).
  2. Seed the pre-seeded clients/users the task needs (read from task.input).
  3. Execute agent_steps in order, capturing HTTP responses.
  4. Call the code_based grader with (ctx, db).
  5. Record pass/fail + transcript.

Emits:
  - evals/transcripts/<task_id>.trial-<N>.json
  - evals/outcomes/pass@k.json
  - prints a summary table to stdout.

Usage:
  python3 evals/run_evals.py --trials 3
  python3 evals/run_evals.py --task 005  --trials 1
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import traceback
import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Disable auth rate limit before importing app (mirrors tests/conftest.py)
os.environ.setdefault("DISABLE_AUTH_RATE_LIMIT", "1")
os.environ.setdefault("APP_ENV", "test")

from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

# Reuse the test fixtures setup
TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://swa:swa@localhost:5432/swa_erp_test",
)

# Import after path setup
from src.backend.core.security import hash_password  # noqa: E402
from src.backend.db.base import Base  # noqa: E402
from src.backend.db.session import get_db  # noqa: E402
from src.backend.main import app  # noqa: E402
from src.backend.models.user import User  # noqa: E402
from src.backend.models.client import Client  # noqa: E402
from src.backend.models.project import Project  # noqa: E402
from src.backend.models.inquiry import Inquiry  # noqa: E402
import src.backend.models  # noqa: F401 - registers all models

from httpx import ASGITransport, AsyncClient  # noqa: E402

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True, future=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


# ---------------------------------------------------------------------------
# DB reset (mirrors tests/conftest.py _reset_tables)
# ---------------------------------------------------------------------------

def _stamp_alembic_head(db: Session) -> None:
    from alembic.config import Config
    from alembic import command
    cfg = Config("src/backend/alembic.ini")
    cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.stamp(cfg, "head")


def _reset_tables(db: Session) -> None:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname='public'"),
        )
        existing = {r[0] for r in result}
        tables = [t for t in Base.metadata.tables.keys() if t in existing]
        if tables:
            try:
                conn.execute(
                    text(f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY CASCADE")
                )
            except Exception:
                conn.rollback()
                for t in tables:
                    conn.execute(text(f"DROP TABLE IF EXISTS {t} CASCADE"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    _stamp_alembic_head(db)


def _fresh_db() -> Session:
    """Wipe + rebuild schema. Returns a session bound to the fresh DB."""
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    db = TestingSessionLocal()
    _reset_tables(db)
    return db


def _override_db(db: Session):
    """Patch FastAPI get_db dependency to return our session."""
    app.dependency_overrides[get_db] = lambda: db


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

def _seed_user(db: Session, email: str, role: str, password: str) -> User:
    u = User(
        email=email,
        name=f"{role.title()} User",
        password_hash=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


async def _login(client: AsyncClient, email: str, password: str) -> str:
    r = await client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return r.json()["access_token"]


async def _seed_clients_for_ambiguous(db: Session):
    """For task 001: create two clients with the same name (ambiguous match)."""
    c1 = Client(name="Ambiguous Test Client", code="AMB-001",
                primary_email="amb1@test.com")
    c2 = Client(name="Ambiguous Test Client", code="AMB-002",
                primary_email="amb2@test.com")
    db.add_all([c1, c2])
    db.commit()
    db.refresh(c1)
    db.refresh(c2)
    return [c1, c2]


# ---------------------------------------------------------------------------
# Step execution
# ---------------------------------------------------------------------------

class StepError(Exception):
    pass


async def _execute_step(client: AsyncClient, step: dict, ctx: dict) -> dict:
    """Execute one agent_step. Returns dict with status, response_body, and captures."""
    actor = step.get("actor", "")
    method = step["action"].split()[0]
    path_template = step["action"].split(maxsplit=1)[1] if " " in step["action"] else step["action"]

    # Resolve $ref placeholders from ctx
    path = _resolve_refs(path_template, ctx)
    body = _resolve_refs(step.get("body"), ctx) if step.get("body") else None

    # Set auth header based on actor
    if actor in ctx.get("_tokens", {}):
        client.headers["Authorization"] = f"Bearer {ctx['_tokens'][actor]}"
    else:
        client.headers.pop("Authorization", None)

    url_path = path if path.startswith("/") else f"/{path}"

    resp = await client.request(method, url_path, json=body)
    result = {
        "status": resp.status_code,
        "response_body": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text,
    }

    # Capture
    captures = step.get("capture", "").split(",")
    for cap in captures:
        cap = cap.strip()
        if not cap:
            continue
        _capture_value(result, resp, cap, step, ctx)

    return result


def _resolve_refs(template, ctx: dict):
    """Resolve $ref: stepN.field.path  in strings (paths) and body values."""
    if template is None:
        return None
    if isinstance(template, str):
        return _resolve_str(template, ctx)
    if isinstance(template, dict):
        return {k: _resolve_refs(v, ctx) for k, v in template.items()}
    if isinstance(template, list):
        return [_resolve_refs(v, ctx) for v in template]
    return template


def _resolve_str(s: str, ctx: dict) -> str:
    """Replace $ref: stepN.field and {stepN.field} placeholders."""
    # $ref: step1.client_id
    def _replace_ref(m):
        steps = m.group(1).split(">")
        step_id = steps[0].strip()
        field_path = steps[1].strip()
        return str(_dig(ctx.get(step_id, {}), field_path))

    s = re.sub(r"\$ref\s+(\S+)", _replace_ref, s)

    # {step1.client_id} in path templates
    def _replace_brace(m):
        inner = m.group(1)
        if "." in inner:
            step_id, field_path = inner.split(".", 1)
            return str(_dig(ctx.get(step_id, {}), field_path))
        return inner

    s = re.sub(r"\{([^}]+)\}", _replace_brace, s)
    return s


def _dig(obj: dict, path: str):
    """Navigate obj.path. Handles 'candidates[0].id' syntax."""
    parts = path.replace("[", ".[").split(".")
    cur = obj
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if p.startswith("["):
            idx = int(p[1:-1])
            cur = cur[idx]
        else:
            cur = cur.get(p)
            if cur is None:
                # Try key with p as-is
                return None
    return cur


def _capture_value(result: dict, resp, cap: str, step: dict, ctx: dict):
    """Capture values from the response into ctx.

    Capture names map to response fields:
      - inquiry_id   -> response_body.id
      - client_id    -> response_body.id
      - project_id   -> response_body.project_id (or result.id)
      - agreement_id -> response_body.id
      - token_id     -> response_body.id
      - docref_id    -> response_body.id
      - error_body   -> entire response body
      - result       -> entire response body
      - timesheet    -> entire response body
      - invoice_id   -> response_body.id
      - invoice      -> entire response body
    """
    step_id = step.get("_step_id", f"step{step.get('step', '?')}")
    rb = result["response_body"]

    field_map = {
        "inquiry_id": "id",
        "client_id": "id",
        "agreement_id": "id",
        "token_id": "id",
        "docref_id": "id",
        "invoice_id": "id",
        "project_id": "project_id",
    }

    # Special: ambiguous candidates come from a 300 error
    if cap == "candidates" or (cap == "error_body" and result["status"] == 300):
        if "candidates" in rb:
            ctx.setdefault("candidates", []).extend(rb["candidates"])
            # Also store under step id for verification
            ctx[step_id] = {"candidates": rb["candidates"], "status": result["status"]}
        else:
            ctx[step_id] = {"response_body": rb, "status": result["status"]}
        return

    if cap in ("result", "timesheet", "invoice", "error_body"):
        ctx[step_id] = {"response_body": rb, "status": result["status"]}
        # Also store under the capture name for convenience
        if cap in ctx[step_id]:
            pass  # don't overwrite
        ctx[step_id][cap] = rb
        return

    field = field_map.get(cap, cap)
    val = _dig(rb, field) if isinstance(rb, dict) else None
    ctx[step_id] = ctx.get(step_id, {})
    ctx[step_id][cap] = val
    ctx[step_id]["response_body"] = rb
    ctx[step_id]["status"] = result["status"]

    # For the ambiguous-match step, store candidate list globally too
    if "candidates" in rb:
        ctx.setdefault("all_candidates", []).extend(rb["candidates"])


async def _run_task_once(task: dict, db: Session) -> dict:
    """Run a single task once with a fresh DB. Returns result dict."""
    ctx: dict = {}
    transcript = []

    # Override DB
    _override_db(db)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Seed users
        admin = _seed_user(db, "admin@swa.co.in", "admin", "admin123!")
        pm = _seed_user(db, "pm@swa.co.in", "pm", "pm123!")
        viewer = _seed_user(db, "viewer@swa.co.in", "viewer", "viewer123!")
        designer = _seed_user(db, "designer@swa.co.in", "designer", "designer123!")
        ctx["_user_ids"] = {
            "admin": str(admin.id), "pm": str(pm.id),
            "viewer": str(viewer.id), "designer": str(designer.id),
        }
        ctx["admin_user_id"] = str(admin.id)

        # Seed ambiguous clients for task 001
        if task["id"].startswith("001-"):
            cands = _seed_clients_for_ambiguous(db)
            ctx["_ambiguous_client_ids"] = [str(c.id) for c in cands]

        # Login all actors
        for actor, email, pw in [
            ("admin", "admin@swa.co.in", "admin123!"),
            ("pm", "pm@swa.co.in", "pm123!"),
            ("viewer", "viewer@swa.co.in", "viewer123!"),
            ("designer", "designer@swa.co.in", "designer123!"),
            ("admin_user", "admin@swa.co.in", "admin123!"),
        ]:
            if email == "admin@swa.co.in" and actor not in ("admin", "admin_user", "pm"):
                continue
            try:
                token = await _login(client, email, pw)
                ctx["_tokens"][actor] = token
            except Exception:
                pass
        ctx.setdefault("_tokens", {})

        # Execute steps
        for step in task.get("agent_steps", []):
            step["_step_id"] = f"step{step['step']}"
            try:
                result = await _execute_step(client, step, ctx)
                transcript.append({
                    "step": step["step"],
                    "actor": step.get("actor"),
                    "action": step["action"],
                    "status": result["status"],
                    "response_body": result["response_body"],
                })
            except Exception as e:
                transcript.append({
                    "step": step["step"],
                    "actor": step.get("actor"),
                    "action": step["action"],
                    "error": f"{type(e).__name__}: {e}",
                })
                ctx[f"step{step['step']}_error"] = str(e)

    # Run grader
    from evals.graders.code_based import get_grader

    grader_id = task.get("verification", "").split(":")[-1].strip() if ":" in task.get("verification", "") else None
    # Fallback: derive grader name from task id
    if not grader_id:
        tmap = {
            "001-inquiry": "001_inquiry_conversion",
            "002-agreement": "002_id_chain",
            "003-rbac": "003_rbac",
            "004-time": "004_time_aggregation",
            "005-invoice": "005_gst",
        }
        for k, v in tmap.items():
            if task["id"].startswith(k.split("-")[0].zfill(3)[:3]):
                grader_id = v
                break

    grader = get_grader(grader_id) if grader_id else None
    if grader is None:
        return {
            "task_id": task["id"],
            "passed": False,
            "error": f"No grader found for {grader_id}",
            "transcript": transcript,
            "evidence": "",
        }

    # Add status codes to ctx for grader 003
    for t in transcript:
        sid = f"step{t['step']}"
        if "status" in t and "_step_id" not in t:
            ctx[f"step{t['step']}_status"] = t["status"]
        # Store step statuses at top level for grader access
        ctx_key = f"step{t['step']}_status"
        ctx[ctx_key] = t.get("status", 0)

    # Map step captures to ctx for grader
    for t in transcript:
        ctx[f"step{t['step']}"] = ctx.get(f"step{t['step']}", {})
        if "response_body" in t:
            ctx[f"step{t['step']}"]["response_body"] = t["response_body"]
            ctx[f"step{t['step']}"]["status"] = t["status"]

    try:
        passed, evidence = grader(ctx=ctx, db=db)
    except Exception as e:
        passed = False
        evidence = f"GRADER EXCEPTION: {type(e).__name__}: {e}\n{traceback.format_exc()}"

    return {
        "task_id": task["id"],
        "passed": passed,
        "evidence": evidence,
        "transcript": transcript,
    }


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def load_tasks() -> list[dict]:
    """Load all task YAML files from evals/tasks/."""
    import yaml
    tasks_dir = Path(__file__).resolve().parent / "tasks"
    tasks = []
    for f in sorted(tasks_dir.glob("*.task.yaml")):
        with open(f) as fh:
            t = yaml.safe_load(fh)
            t["_file"] = str(f)
            tasks.append(t)
    return tasks


def write_transcript(task_id: str, trial: int, result: dict) -> None:
    out_dir = Path(__file__).resolve().parent / "transcripts"
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"{task_id}.trial-{trial}.json"
    with open(path, "w") as fh:
        json.dump(result, fh, indent=2, default=str)


def write_outcomes(all_results: list[dict]) -> None:
    out_path = Path(__file__).resolve().parent / "outcomes" / "pass@k.json"
    out_path.parent.mkdir(exist_ok=True)
    # Aggregate
    tasks = {}
    for r in all_results:
        tid = r["task_id"]
        if tid not in tasks:
            tasks[tid] = {"trials": 0, "passes": 0}
        tasks[tid]["trials"] += 1
        if r["passed"]:
            tasks[tid]["passes"] += 1

    summary = []
    for tid, stats in tasks.items():
        pass_at_k = stats["passes"] / stats["trials"] if stats["trials"] > 0 else 0
        pass_k = stats["passes"] / stats["trials"] if stats["trials"] > 0 else 0
        summary.append({
            "task_id": tid,
            "pass@k": round(pass_at_k, 3),
            "pass^k": round(pass_k, 3),
            "passes": stats["passes"],
            "trials": stats["trials"],
        })

    with open(out_path, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"\nOutcomes written to {out_path}")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Run wave-43 evals")
    parser.add_argument("--trials", type=int, default=3, help="Trials per task (default: 3)")
    parser.add_argument("--task", type=str, default=None, help="Run only one task (by prefix)")
    args = parser.parse_args()

    import asyncio
    import yaml

    tasks = load_tasks()
    if args.task:
        tasks = [t for t in tasks if t["id"].startswith(args.task)]

    if not tasks:
        print("No tasks found in evals/tasks/")
        sys.exit(1)

    print(f"Running {len(tasks)} eval tasks x {args.trials} trials each")
    print(f"DB: {TEST_DATABASE_URL}\n")

    all_results = []
    summary_lines = []

    for task in tasks:
        task_passes = 0
        task_trials = 0
        for trial in range(1, args.trials + 1):
            # Fresh DB per trial
            db = _fresh_db()
            ctx = {"_tokens": {}, "_user_ids": {}}
            result = asyncio.run(_run_task_once(task, db))
            db.close()

            task_trials += 1
            if result["passed"]:
                task_passes += 1

            write_transcript(task["id"], trial, result)
            status = "PASS" if result["passed"] else "FAIL"
            print(f"  [{task['id']}] trial {trial}/{args.trials}: {status}")
            if not result["passed"]:
                print(f"    evidence: {result.get('evidence', result.get('error', 'N/A'))[:500]}")
                if result.get("error"):
                    print(f"    error: {result['error']}")

            all_results.append(result)

        pass_k = task_passes / task_trials
        line = f"{task['id']}: {task_passes}/{task_trials} = pass@k {pass_k:.0%}, pass^k {pass_k:.0%}"
        summary_lines.append(line)

    print("\n" + "=" * 70)
    print("EVAL SUMMARY")
    print("=" * 70)
    for line in summary_lines:
        print(f"  {line}")
    print("=" * 70)

    summary = write_outcomes(all_results)
    overall = sum(1 for s in summary if s["passes"] == s["trials"]) / len(summary) if summary else 0
    print(f"\nOverall deterministic pass rate (pass^k for all tasks): {overall:.0%}")
    if summary:
        for s in summary:
            marker = "✅" if s["pass@k"] == 1.0 else ("⚠️" if s["pass@k"] > 0 else "❌")
            print(f"  {marker} {s['task_id']}: pass@k={s['pass@k']:.0%} pass^k={s['pass^k']:.0%} ({s['passes']}/{s['trials']})")


if __name__ == "__main__":
    main()
