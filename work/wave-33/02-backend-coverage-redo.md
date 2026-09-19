# Wave-33 Task 02 — Backend coverage REDO (previous attempt fabricated)

**Read `work/wave-33/01-backend-coverage.report.md` FIRST.** A previous session claimed 5 test
files existed with specific pass/fail numbers (66% import_service coverage, 11/12 tests passing).
**None of those files existed on disk.** The claim was fabricated — caught during independent
verification, not by the reporting session itself. This wave redoes the work for real. Every
number in your report must come from a command you actually ran and can show output for.

## Current real baseline (verified 2026-08-19 on `main`, commit `30f68aa`)

```
python3 -m pytest tests/ -q --cov=src/backend --cov-report=term
TOTAL: 8698 stmts, 1615 missed, 81% overall
```

| Module | Coverage | Target |
|---|---|---|
| `services/pdf_service.py` | **17%** | ≥70% |
| `services/quote_service.py` | **21%** | ≥70% |
| `services/import_service.py` | **65%** | ≥70% |
| `services/task_service.py` | **58%** | ≥70% |
| `services/notification_service.py` | **50%** | ≥70% |

Priority order: `pdf_service` → `quote_service` → `import_service` → `task_service` →
`notification_service`.

Also present and unrelated to this wave (do not try to fix): 5 pre-existing test failures
(`tests/wave-22/test_rbac_gaps.py::TestMaterialsAuth` x3, `tests/wave-4/test_task_assignments.py::test_assign_unauthorized`,
`tests/wave-8/test_reports_api.py::test_unauthorized_401`) — all assert unauthenticated requests
return 401; FastAPI's `HTTPBearer` returns 403 with no header present. Known tech debt, not yours
to fix here.

## Files to create
- `tests/wave-33/test_pdf_service.py`
- `tests/wave-33/test_quote_service.py`
- `tests/wave-33/test_import_service.py`
- `tests/wave-33/test_task_service.py`
- `tests/wave-33/test_notification_service.py`
- `tests/wave-33/conftest.py` **only if needed** — check whether the main `tests/conftest.py`
  (Postgres-backed, `setup_test_db` autouse fixture) already works for these tests before
  building a separate SQLite path. A previous attempt built a SQLite conftest that worked in
  isolation but was never actually reconciled with the real suite — prefer using the main
  conftest directly if it works, it's simpler and matches every other wave's tests.

## The work

Use the `superpowers:test-driven-development` skill. Test real behavior (status transitions,
PDF content, malformed input handling, idempotency), not just line execution. Follow the existing
patterns in `tests/wave-*/test_*.py` for fixture/client setup.

## Non-negotiable process (this is why the previous attempt failed)

1. **After writing each test file, immediately run it** and paste the real output before moving
   to the next file. Do not write all 5 files then run once at the end — if you get interrupted,
   partial-but-verified beats complete-but-unverified.
2. **Commit after each file passes**, not just at the end. `git add tests/wave-33/test_X.py &&
   git commit -m "wave-33: test_X coverage"`. This project has repeatedly lost work to session
   crashes/hangs — frequent commits are how you protect your own progress.
3. Before writing your final report, run `find tests/wave-33 -type f` and paste the output, then
   run the full coverage command below and paste that exact output. Do not describe results from
   memory.

## Acceptance criteria
- [ ] `find tests/wave-33 -type f` shows all 5 test files (+ conftest if needed) — paste output
- [ ] `python3 -m pytest tests/wave-33/ -v` — paste full output, all passing
- [ ] `python3 -m pytest tests/ -q --cov=src/backend --cov-report=term` — paste the per-module
      coverage lines for all 5 target modules — target ≥70% each, ≥85% overall
- [ ] No module below 70%
- [ ] Full suite still green (baseline: 445 passed, 1 skipped, 8 pre-existing/unrelated failures
      — do not let that number get worse)

## Deliver
Report → `work/reports/wave-33/02-backend-coverage-redo.report.md`. Every number must have the
command that produced it right above or below it in the report. Commit before writing the report.

## Constraints
- Time budget: 180 min
- Commit frequently (see above) — this is not optional given this wave's history
- Allowed: file edit, git, pytest
