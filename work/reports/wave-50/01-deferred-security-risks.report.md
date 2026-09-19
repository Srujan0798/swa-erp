# Wave-50 Task 01 Report — Close two deferred wave-37 security RISKs (ROUND 5 task A)

- **HEAD:** `38cb8a8` (BACKLOG close commit; report itself uncommitted by design)
- **Status:** DONE — both findings fixed, guarded, BACKLOG rows closed.

## Shape choice (item 1): (b) `export_jobs` table — as preferred by the brief

`result_expires=3600` is set on the Celery app (`src/backend/workers/celery_app.py:13`),
so result-backend metadata would go stale and could fail open. The table survives
expiry. Cost: one Alembic migration (`0035`, linear head — another agent's `0036`
chains on it, verified single head via `ScriptDirectory.get_heads() == ['0036']`).

- Ownership enforced in `src/backend/api/jobs.py::_require_job_owner`: **404 on
  mismatch (not 403**, so a non-owner cannot confirm the id exists); **admins bypass
  explicitly** (stated in code comment + here).
- Unknown ids / pre-ownership rows keep legacy handling (status → `pending`,
  result → 404) — preserves wave-31 compat
  (`test_job_status_unknown_job_returns_pending` still passes).

## Commits (per numbered item)

| Item | Commit | Content |
|------|--------|---------|
| 1 (SEC-07 code) | `3d619b9` | model + migration 0035 + exports enqueue + jobs enforcement |
| 2 (metrics flag) | `8652036` | `METRICS_REQUIRE_AUTH` + `_metrics_guard` + docs + `.env.example` + dev compose + prometheus comment |
| 3 (tests) | inside `aa03e77` | **NOT my commit.** A concurrent lint/format agent swept the whole worktree (incl. my then-untracked test files, verbatim) into their frontend commit. Their only changes to my files: 1 trailing newline (jobs.py), 1 dropped redundant `# noqa` (main.py). My separate test commit failed with "nothing to commit" because the files were already committed. Content verified identical to what I wrote. |
| 4 (BACKLOG) | `38cb8a8` | closes exactly the 2 rows (see below) |

Full hashes: `3d619b9…`, `8652036…`, `aa03e77f1e75a5c0380fdc93987f426c2c4ec2d8`,
`38cb8a820192a6f4e3469070f0663b7475074e97`.

## Files changed (mine only)

- `src/backend/models/export_job.py` (new), `src/backend/models/__init__.py`
- `src/backend/alembic/versions/0035_export_job_ownership.py` (new)
- `src/backend/api/exports.py` (`_record_export_job` at all 3 async enqueue points)
- `src/backend/api/jobs.py` (ownership check on both GETs + `get_db`)
- `src/backend/core/config.py` (`METRICS_REQUIRE_AUTH: bool = True`)
- `src/backend/main.py` (runtime `_metrics_guard`; old `Depends(get_current_user)` replaced so the flag is read per-request and tests can toggle it)
- `tests/wave-50/test_job_ownership.py`, `tests/wave-50/test_metrics_auth.py` (new)
- `docs/operational/OBSERVABILITY.md`, `.env.example`, `docker-compose.dev.yml`, `prometheus.yml` (metrics flag docs + dev scraper)
- `BACKLOG.md` (2 rows only)
- Untouched per constraints: `services/*`, `api/documents.py`, `src/frontend/`, `tests/wave-49/`.

## Metrics / Prometheus (item 2)

- `prometheus.yml` scrapes `backend:8000/metrics` with **no auth** → broken by the
  secure default. No Prometheus service exists in base/prod compose; only the
  **optional dev service** in `docker-compose.dev.yml` uses it. Per the brief I set
  `METRICS_REQUIRE_AUTH=false` **in that dev file only** (trusted local network) and
  noted it in the file + `OBSERVABILITY.md`. Base + prod keep the default `true`.
- Operator note: on any network where Prometheus cannot present a JWT, set
  `METRICS_REQUIRE_AUTH=false` for the scraped backend **only if that network is
  trusted/internal**; otherwise run an authenticated sidecar. Never open it on an
  externally reachable port.

## Tests — pass output (post-fix, isolated DB `swa_erp_test_w50`, dropped after)

```
tests/wave-50/test_job_ownership.py::test_owner_reads_own_job_status PASSED
tests/wave-50/test_job_ownership.py::test_owner_downloads_own_job_result PASSED
tests/wave-50/test_job_ownership.py::test_other_pm_gets_404_on_job_status PASSED
tests/wave-50/test_job_ownership.py::test_other_pm_gets_404_on_job_result PASSED
tests/wave-50/test_job_ownership.py::test_admin_bypasses_ownership_check PASSED
tests/wave-50/test_job_ownership.py::test_unknown_job_id_still_returns_pending PASSED
tests/wave-50/test_metrics_auth.py::test_metrics_unauthenticated_rejected_by_default PASSED
tests/wave-50/test_metrics_auth.py::test_metrics_authenticated_returns_prometheus_text PASSED
tests/wave-50/test_metrics_auth.py::test_metrics_open_when_flag_false PASSED
tests/wave-50/test_metrics_auth.py::test_metrics_auth_restored_after_flag_reset PASSED
======================== 10 passed ========================
```

Wave-50 + wave-36 (metrics compat) together: **45 passed, 2 skipped** (the 2 skips are
the Redis-coupled readyz tests — Redis is DOWN in this env, a documented PARKED item).

## Pre-fix failure proof (4 fix files checked out at `fda369e`, tests kept, then restored)

- All 5 ownership tests ERROR: `AssertionError: enqueue did not record an ExportJob ownership row`.
- 3 metrics tests FAIL: `AttributeError: 'Settings' object has no attribute 'METRICS_REQUIRE_AUTH'`
  (`test_metrics_open_when_flag_false`, `test_metrics_auth_restored_after_flag_reset`,
  `test_metrics_unauthenticated_rejected_by_default`).
- The other 2 metrics tests + unknown-job test pass pre-fix (auth/pending already
  behaved that way) — reported honestly; the files as a whole fail pre-fix (8 fail/error of 11).
- Post-restore re-run: 10/10 pass.

## Full suite — no regression (same isolated DB)

`pytest tests/ --ignore=e2e,performance,wave-4/test_task_assignments.py`:
**28 failed, 562 passed, 9 skipped.** The 28 failures are **byte-identical pre/post
fix** (failing-ID diff empty; baseline run of the same subset at `fda369e` also
28 failed): 22× wave-6 documents + 1× wave-31 storage round-trip (concurrent agent's
uncommitted `api/documents.py` WIP — not my files), 4× wave-31 project-eager tests
(pre-existing transaction-visibility flaw, fails without my diff — verified), 1×
wave-13 CLI dry-run, 2× wave-9 gapless-concurrency (timing-sensitive under parallel load).
Zero regressions attributable to this task. Wave-4 file excluded: it **hangs
indefinitely with Redis down** (a concurrent agent's wave-4-only run froze identically
before my changes; mine hung 25+ min at the same file) — environmental, not a defect.
`tests/wave-1/test_auth.py::test_logout_revokes_refresh` is flaky in this shared
worktree (failed once, passed in the full run; fails identically with my files
reverted — concurrent agent has uncommitted `services/auth_service.py` WIP).

## BACKLOG rows closed (item 4, commit `38cb8a8`)

- `SF-4 / SEC-02` → **CLOSED** (code `8652036`, guard `test_metrics_auth.py`).
- Combined `SEC-07/08` row **split**: `SEC-07` → **CLOSED** (code `3d619b9`, guard
  `test_job_ownership.py`); `SEC-08` (document write roles) stays **RISK** — out of
  scope per brief. No other rows touched.

## DoD

- [x] `pytest tests/wave-50/ -v` green (10/10), plus wave-36 compat green
- [x] Pre-fix failure proven (stash-equivalent via `checkout fda369e -- <4 files>`, restore verified)
- [x] Full suite: no new failures (identical-28 proof)
- [x] Compose/prometheus diff shown above + operator note
- [x] BACKLOG: exactly the 2 rows closed, rest untouched
- [x] Constraints respected (no services/documents/frontend/wave-49 touches)

## Risks / notes for orchestrator

1. **Shared `swa_erp_test` DB is a deadlock zone under parallel pytest** (DROP SCHEMA
   vs unique-email INSERTs froze 2 agents' runs with zero CPU progress). I ran on a
   private `swa_erp_test_w50` via a `-p` plugin (no repo files touched), then dropped
   it. Recommend serializing DB-touching waves or per-wave databases.
2. **Cross-agent commit sweep** (`aa03e77`) committed my tests + cosmetic edits to my
   files. Harmless here, but `git add -A`-style sweeps during parallel waves can
   misattribute work and caused my test-commit to no-op.
3. **Redis down** → wave-4 hang + readyz skips. Needs infra, not code.
4. `ruff check` on all my files: clean.
