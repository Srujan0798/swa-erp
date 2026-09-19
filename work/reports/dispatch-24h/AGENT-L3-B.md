# AGENT-L3-B

Worktree: `/Users/srujansai/Desktop/swa-erp-wt-l3-b` (uncommitted working-tree changes, ready for user merge pick)
Scope: L3-B only — SA is a **yearly retainer per client, not per project**; tokens are work units under that SA; UI copy must say this. Integrator closeout: original OpenCode agent died mid-run after writing the changes but before verification/report.

## Implemented (in worktree, NOT on main)

**UI copy — "yearly retainer per client":**
- `AgreementForm.tsx`: card header states "A service agreement is a yearly retainer per client, not per project. Tokens are work units under this agreement. Use the agreed dates; leave the end date blank if unknown."
- `AgreementsTab.tsx`: "Each service agreement is a yearly retainer for this client, not per project. Expand an agreement to see its token work units (e.g. for INSUDESIGN)." Open-ended → "(end date not recorded)".
- `AgreementsPage.tsx` / `TokensPage.tsx` sheet descriptions updated with the same rule.
- `TokenForm.tsx`: "Tokens are work units under the client's yearly retainer service agreement. A linked project is optional context and must belong to the same client."

**Code enforcement (project linked to a token must belong to the agreement's client):**
- `token_service.py`: `_validate_project_context` on create and on update; 422 when project belongs to another client or is missing. Clearing `project_id` on update now persists (explicit `db.commit()`).
- `TokenForm` project picker is scoped: `api.listProjects({ client_id })` — only the agreement's client's projects are offered (client context passed from `AgreementsTab`/`TokensPage` via new `clientId` prop).
- Schemas (`agreement.py`, `token.py`): field descriptions only — no behavioral schema change, no migration needed.

**Tests added:**
- `tests/wave-9/test_tokens.py`: `TestTokenProjectOwnership` — 7 cases (same-client ok, projectless ok, other-client rejected on create + update, update accept/clear, one agreement spanning two projects + a projectless token).
- Frontend: `Forms.test.tsx` (project request scoped to client; no request without client), `AgreementsTab.test.tsx` + `TokensPage.test.tsx` (copy assertions).

## Verification (fresh pastes, Python 3.11.5, Postgres localhost:5432)

- `python3.11 -m pytest tests/wave-9/test_tokens.py::TestTokenProjectOwnership -v` → **7/7 passed**.
- `python3.11 -m pytest tests/wave-9/test_tokens.py -v` → **23 passed, 1 failed** (pre-existing `TestTokenConcurrency` gapless-ID test — **fails identically on main**; pre-existing harness issue, DEFER L8).
- `npx vitest run` (3 touched suites) → **Test Files 3 passed, Tests 32 passed**.
- `ruff check` (3 backend files) → All checks passed. `black --check` → 3 files unchanged.
- `eslint` (6 touched frontend files) → clean. `tsc --noEmit` → no errors in touched files.

## BLOCKED / NOT MEASURED / DEFER

- Live `:3100` click-through: NOT MEASURED (L2/L3 code is in worktrees; main app does not include these changes until merge).
- Pre-existing concurrency-test failures: **DEFER L8** (quality seal should fix the harness or mark environmental).
- No commit, no staging, no push, no Docker, no seed-demo. Merge of this worktree needs **user pick** (per L10-C).