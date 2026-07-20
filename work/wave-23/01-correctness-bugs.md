# Task 01 — Correctness bugs (found by 2026-07-21 full-project audit)

## What to do
Fix confirmed correctness bugs — each has a file:line citation from a full-codebase audit, not
speculative.

## Files to modify
- MODIFY: `src/backend/services/export_service.py`
- MODIFY: `src/backend/api/lifecycle.py`
- MODIFY: `src/backend/db/repositories/task_repo.py`
- MODIFY: `src/backend/models/project.py`
- CREATE: new Alembic migration for the Project `version` column
- MODIFY: `src/backend/services/project_service.py` (or wherever project updates happen, to
  actually use the new version column for optimistic locking)
- CREATE/MODIFY: `tests/wave-23/test_correctness_fixes.py`

## Files you must NOT touch
- `src/backend/models/document.py` and its dead `deleted_at` column — that's a separate,
  lower-risk cleanup item, deliberately left OUT of this task to keep this one focused; leave it
  as-is here (it's harmless dead code, not a bug that affects behavior)

## The core problem (inline)

### 1. Fabricated numbers in the financial report PDF — most severe finding in this task
`src/backend/services/export_service.py:209-213` (approximate lines — verify exact location by
reading the file), the "Net Profit & Loss (Estimated)" section of the financial report PDF does:
```python
_kv_row("Estimated Costs:", _fmt_decimal(total_revenue * Decimal("0.7")))
_kv_row("Net P&L:", _fmt_decimal(net * Decimal("0.3")))
```
This fabricates costs and profit as flat 70%/30% ratios of revenue, completely ignoring the real
per-project cost data that already exists via `project_pnl`/`ProjectCost` (see
`src/backend/services/project_pnl_service.py` or equivalent — check the actual module name/
location, it was audited as existing and correct). This PDF is handed to users as a real
financial report. Fix: replace the hardcoded ratio with a real aggregation query pulling actual
`ProjectCost` totals per project (or across the reporting scope this export covers), computing
real costs and real net P&L the same way `project_pnl_service` already does for the per-project
view. Do not ship a report with invented numbers.

### 2. Money handled as float instead of Decimal
`src/backend/api/lifecycle.py:27` declares `total_estimated_value: float` in
`ProjectStatsResponse`, and line 72 does `float(total_estimated)` — converting a
`Decimal(18,2)` sum to a Python float before returning it, violating this project's own "All
money: Decimal(18,2)" convention (see `CLAUDE.md` domain rules). Fix: change the field type to
`Decimal` in the schema and remove the `float()` cast — return the Decimal directly (Pydantic v2
serializes Decimal to JSON correctly without precision loss, unlike float).

### 3. Task's "soft delete" is actually a hard delete
`src/backend/db/repositories/task_repo.py`'s `soft_delete()` function (around lines 229-235)
does `db.delete(task); db.flush()` — a real hard delete — despite the `Task` model having a
`deleted_at` column (`models/task.py:47`) that's never set or read anywhere in the task stack.
Fix: change `soft_delete()` to actually set `task.deleted_at = datetime.now(UTC)` (use timezone-
aware, not the deprecated `utcnow()` — check how other repos in this codebase already do this
correctly, e.g. grep for `datetime.now(` vs `datetime.utcnow()` usage patterns) and commit,
instead of calling `db.delete()`. Also add a `deleted_at IS NULL` filter to the task list/get
queries in the same file (currently absent — confirmed by the audit, soft-deleted tasks would
currently still show up in lists if this weren't also being hard-deleted).

### 4. Project has no optimistic-locking version column
Confirmed: `src/backend/models/project.py` has no `version` field, despite
`plan/ARCHITECTURE.md`'s failure-points table citing this as the mitigation for "two PMs edit
same project" (now corrected in that doc to say this is NOT implemented — this task actually
implements it). Add a `version: Mapped[int] = mapped_column(nullable=False, default=1,
server_default="1")` column (mirror the exact pattern already used on `BOQ`, `Document`,
`ComplianceItem`, `Quote`, or `User` — check one of those models for the established convention
in this codebase before writing a new one). Add a new Alembic migration. Wire up actual
optimistic-locking enforcement in the project update path: increment `version` on every update,
and if the client's update also specifies an `If-Match`/expected version that doesn't match
current, reject with 409 — check if any other model with a `version` column already has this
enforcement pattern built (e.g. Quote or BOQ) and mirror it; if none of them actually enforce it
either (just track the number without checking it), implement the check fresh for Project and
note in the report whether other models have the same "tracks version but never checks it" gap
(flag, don't fix those others in this task — out of scope).

## Acceptance criteria
- [ ] The financial report PDF's cost/profit figures come from real `ProjectCost` data, not a
  hardcoded ratio — verify by creating a project with known cost entries and confirming the PDF
  reflects them, not `revenue * 0.7`
- [ ] `ProjectStatsResponse.total_estimated_value` is `Decimal` in the schema, no `float()` cast
  remains in `lifecycle.py`
- [ ] Deleting a task sets `deleted_at`, does NOT remove the row from the database (verify with
  a direct DB query after calling the soft-delete path)
- [ ] A soft-deleted task no longer appears in task list/get queries
- [ ] `Project` model has a `version` column; two concurrent updates to the same project with a
  stale expected version correctly reject the second one with 409 (or whatever pattern matches
  the existing convention — document exactly what you implemented in the report)
- [ ] `python3 -m pytest tests/ -q` — 324+ pass — **run with no other pytest process active and
  a freshly reset test DB**, see `docs/PROJECT_HISTORY.md` for why this matters
- [ ] `ruff check` on all touched files — clean

## How to deliver
1. Fix all 4 items
2. Write `tests/wave-23/test_correctness_fixes.py` covering each
3. Run every acceptance check
4. Write report to `work/reports/wave-23/01-correctness-bugs.report.md`
5. Stop

## Constraints
- Time budget: 100 min
- Don't touch `models/document.py`'s dead `deleted_at` column — separate task, out of scope here
- Allowed tools: file edit, pytest, ruff, psql
