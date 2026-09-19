# AGENT-L3-D

Worktree: `/Users/srujansai/Desktop/swa-erp-wt-l3-d` (uncommitted working-tree changes + migration 0037, ready for user merge pick)
Scope: L3-D only — time + doc-ref may be **non-project** (nullable project; no marketing UI built); sustainability recorded **after project completes**. Integrator closeout: original OpenCode agent finished the frontend half, died before backend + verification/report.

## Implemented (in worktree, NOT on main)

**Backend — nullable project end-to-end:**
- Models: `time_tracking.py` `TimeEntry.project_id` and `document_reference.py` `DocumentReference.project_id` → `nullable=True` (`Mapped[uuid.UUID | None]`).
- Schemas: `TimeEntryCreate.project_id` / `TimeEntryRead.project_id`, `DocumentReferenceCreate.project_id` / `DocumentReferenceRead.project_id` → optional/nullable.
- Services: `time_service.create_time_entry_service` skips project 404-check when `project_id is None`; `_entry_to_read` guards null (project_name None). `document_reference_service` skips `ProjectNotFoundError` when None; audit `after_json` guards null. `api/document_references._to_read` guards null (project_code None).
- Migration **0037_nullable_project_time_docref** created and **applied to dev DB** (`alembic heads` → single head `0037`; dev DB alembic_version = 0037). Nullability relax only, zero data change.

**Frontend (from original agent + one integrator fix):**
- Time: `TimeEntryForm`/`TimeTrackingPage` project optional ("Non-project" option, sends `null`); `TimeEntryList` shows "Non-project"; edit freezes project select. Integrator fix: update payload **omits** `project_id` (backend `TimeEntryUpdate` has no such field; test asserted it).
- Doc refs: `DocumentReferenceForm`/`DocumentReferencesPage` project optional with "Non-project" option, sends `null`; empty-state copy "(project optional)".
- Sustainability: `SustainabilityManager` gated — Add/Edit/Delete hidden until project **Closed** (banner: "Read-only: project not Closed"), viewer read-only, `ProjectDetailPage` + `SustainabilityPage` pass `projectStatus`.
- Types: `TimeEntry/TimeEntryCreate/TimeEntryUpdate`, `DocumentReference/Create` → `project_id: string | null`.

**Tests added:** `TestDocumentReferenceNonProject` (4: create without/explicit-null project, unknown still 404, list shows null rows) + 3 time tests (create without project, list includes, unknown still 404).

## Verification (fresh pastes, Python 3.11.5, Postgres localhost:5432)

- `pytest tests/wave-7/test_time_tracking.py tests/wave-9/test_document_references.py` → **43 passed** (incl. 7 new null-project tests).
- `pytest tests/wave-7/test_time_tracking.py` → **16 passed** (incl. 3 new null-project tests).
- `pytest tests/wave-9/test_document_references.py` → **27 passed** (incl. 4 new non-project tests).
- `pytest tests/wave-9/test_tokens.py` → 81 passed, 2 failed = `TestTokenConcurrency` gapless test (**fails identically on main**; pre-existing harness issue, DEFER L8).
- `pytest tests/test_migrations.py` → **27 passed** (dev DB at head 0037, upgrade-head schema valid).
- `npx vitest run` (7 touched suites) → **Test Files 6 passed, Tests 46 passed**.
- `ruff check` (9 backend/test files) → All checks passed. `black --check` → all unchanged (after reformat). `eslint` (8 touched files) → clean. `tsc --noEmit` → no errors in touched files.

## BLOCKED / NOT MEASURED / DEFER

- Backend enforcement of "sustainability only after Closed" would break wave-10 contracts (`test_project` fixture has no status) → frontend gating only; **DEFER** to a future wave decision.
- Live `:3100` click-through of non-project flows: NOT MEASURED (changes in worktree, not merged).
- Pre-existing `TestTokenConcurrency` failure: **DEFER L8**.
- No commit, no staging, no push, no seed-demo. Merge of this worktree needs **user pick** (per L10-C).