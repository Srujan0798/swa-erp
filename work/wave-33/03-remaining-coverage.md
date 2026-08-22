# Wave-33 Task 03 — Finish backend coverage (last 2 of 5 modules)

3 of 5 target modules are already done and merged to `main` (verified independently, not
self-reported): `pdf_service` 100%, `quote_service` 97%, `import_service` 73%. This wave finishes
the remaining 2.

## Current real baseline (verified 2026-08-22 on `main`, commit `41e2b96`)

```
python3 -m pytest tests/ -q --cov=src/backend --cov-report=term
```

| Module | Coverage | Target |
|---|---|---|
| `services/task_service.py` | **58%** | ≥70% |
| `services/notification_service.py` | **50%** | ≥70% |

Overall backend coverage is already 85% (met). The only remaining gap is these 2 modules
individually falling below the "no module under 70%" bar.

Also present, pre-existing, not yours to fix: 5 known failures asserting `401` where FastAPI's
`HTTPBearer` correctly returns `403` for a missing auth header
(`tests/wave-22/test_rbac_gaps.py::TestMaterialsAuth` x3,
`tests/wave-4/test_task_assignments.py::test_assign_unauthorized`,
`tests/wave-8/test_reports_api.py::test_unauthorized_401`).

## Files to create
- `tests/wave-33/test_task_service.py`
- `tests/wave-33/test_notification_service.py`

Follow the patterns already in `tests/wave-33/test_pdf_service.py`,
`test_quote_service.py`, `test_import_service.py` (already on `main`) — same conftest, same
fixture style. Note: `pyproject.toml` already has `--import-mode=importlib` added (needed to
collect wave-33 tests without collision) — don't remove it.

## The work

Use the `superpowers:test-driven-development` skill. Test real behavior:
- `task_service`: creation, status transitions, comment threading, bulk assign/unassign,
  reorder, dependency handling — check `src/backend/services/task_service.py` for the actual
  surface before writing tests.
- `notification_service`: `task_assigned`, `status_changed`, `task_commented` notification
  creation and content — check `src/backend/services/notification_service.py` for the actual
  surface.

## Non-negotiable process (this project has a documented history of exactly this failing)
1. After writing each test file, run it immediately and paste the real output before moving on.
2. **Commit after each file passes**, not just at the end.
3. Before writing your report, run `find tests/wave-33 -type f` and the full coverage command
   below, and paste the actual output. Every number in the report must come from a command you
   ran, not from memory or estimation.

## Acceptance criteria
- [ ] `python3 -m pytest tests/wave-33/ -v` — paste full output, all passing
- [ ] `python3 -m pytest tests/ -q --cov=src/backend --cov-report=term` — paste the per-module
      lines for `task_service` and `notification_service` — target ≥70% each
- [ ] Overall backend coverage still ≥85%, and full suite failure count is still exactly the 5
      pre-existing/unrelated failures (not more, not fewer claimed without proof)

## Deliver
Report → `work/reports/wave-33/03-remaining-coverage.report.md`. Commit before writing the report.

## Constraints
- Time budget: 120 min
- Commit every 10-15 minutes
- Allowed: file edit, git, pytest
