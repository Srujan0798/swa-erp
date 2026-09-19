# Wave-50 Task 01 — Close two deferred wave-37 security RISKs (job IDOR + unauthenticated /metrics)

These two were found by the wave-37 adversarial review, **deliberately deferred as documented RISK**, and recorded in `BACKLOG.md`. They were never closed. Both are still live in the code — verified 2026-08-29, not carried forward from the old report.

## Finding 1 — SEC-07: Job IDOR (any PM can read any other user's export)

`src/backend/api/jobs.py` — both endpoints authorize by **role only**, never by ownership:

```python
@router.get("/{job_id}")
def get_job_status(
    job_id: str,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
) -> dict:
    result = AsyncResult(job_id, app=app)
```

`current_user` is bound and then **never used**. `get_job_result` (same file) has the identical shape and additionally streams the file back via `get_storage().read(result_key)`.

Confirmed the ownership data does not exist yet either: `grep -rn "user_id\|owner" src/backend/workers/*.py` → **0 hits**. Celery tasks record no owner, so there is currently nothing to check against.

**Impact:** any authenticated PM-or-above who guesses or observes a `job_id` can read the status of, and download, another user's exported file. Exports can contain client lists, invoices, and time data.

## Finding 2 — SF-4 / SEC-02: `/metrics` is unauthenticated

`src/backend/main.py:111`:
```python
@app.get("/metrics", include_in_schema=False)
```
No auth dependency. The wave-37 justification ("VPN/internal deploy") is reasonable **as a deployment assumption**, but the deployment is external and unconfirmed (Viraj holds the server facts — see `HANDOFF.md`). Shipping a submission that assumes a network perimeter nobody has verified is exactly the kind of unstated assumption an evaluator will flag.

## Files you own
- `src/backend/api/jobs.py`
- `src/backend/workers/` (whichever task module enqueues exports)
- `src/backend/main.py` (the `/metrics` route only)
- `src/backend/core/config.py` (one new setting)
- `tests/wave-50/test_job_ownership.py` (new)
- `tests/wave-50/test_metrics_auth.py` (new)

## The work

### 1. Give jobs an owner, then enforce it
Record the enqueuing user's id when an export task is created, and check it on read. Two viable shapes — **pick one and say why in your report**:

- **(a) Celery task kwarg + result metadata.** Pass `user_id` into the task, store it in the task's result backend metadata, compare against `current_user.id` on read.
- **(b) A small `export_jobs` table** (`job_id`, `user_id`, `created_at`) written at enqueue time, read on status/result. Needs an Alembic migration.

(b) is more robust and survives a Celery result-backend expiry; (a) is smaller. Either is acceptable — **(b) is preferred** if the result backend has a TTL, because an expired result would otherwise fail open.

On mismatch return **404, not 403** — a 403 confirms the job id exists, which is itself a small leak. Admins may bypass the ownership check; say so explicitly in the code and the report.

### 2. Put `/metrics` behind an opt-in setting
Add `METRICS_REQUIRE_AUTH: bool = True` to config (default **True** — secure by default). When true, `/metrics` requires a valid token; when explicitly set false, it serves openly for a Prometheus scraper on a trusted network. Document the flag in `docs/operational/OBSERVABILITY.md` and in `.env.example`, including the one-line reason an operator would set it false.

Check whether `docker-compose`/`prometheus.yml` scrape `/metrics` — if so, either give the scraper a token or set the flag false **in that compose file specifically**, and note it. Do not silently break the existing observability stack.

### 3. Prove both with tests
- `test_job_ownership.py`: user A enqueues a job; user B (also a PM) requests that `job_id` on **both** `/api/jobs/{id}` and `/api/jobs/{id}/result` → both 404. User A gets their own job fine. An admin can read it.
- `test_metrics_auth.py`: with the flag default (True), unauthenticated `/metrics` → 401/403; authenticated → 200 and returns Prometheus text. With the flag false, unauthenticated → 200.

### 4. Update the RISK register
Both rows in `BACKLOG.md` ("Wave-37 deferred RISKs" table, SF-4 / SEC-02 and SEC-07) move from RISK to **CLOSED**, each with the commit hash and the test that now guards it. Do **not** touch the other rows in that table — they are still open and must stay listed.

## Acceptance criteria
- [ ] `python3 -m pytest tests/wave-50/ -v` — paste real output, all green
- [ ] Each new test **fails against the pre-fix code** — prove it (stash the fix, run, paste the failure), then passes after
- [ ] Full backend suite green, no regression
- [ ] If a Prometheus scraper existed and you changed its config, show the compose/prometheus diff and say what an operator must now do
- [ ] `BACKLOG.md` updated: exactly those two rows closed, the rest untouched

## Deliver
`work/reports/wave-50/01-deferred-security-risks.report.md`. Commit before writing it.

## Constraints
- Time budget: 150 min · commit per numbered item
- Secure by default: if you find yourself defaulting a security flag to the permissive value, stop and reconsider
- Do **not** attempt the other deferred RISKs (SF-6/7 import savepoints, SEC-04/05 RBAC, SEC-08 document write roles) — they are separately scoped and out of bounds here
- SEC-04/05 in particular was re-checked 2026-08-29 and is **not** a defect as written: `src/backend/api/time_entries.py` already gates reads with `require_role(Role.PM)`. Leave it alone; it is a product call for Viraj, not a bug
