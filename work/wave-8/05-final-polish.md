# Task 05 — Final Integration + Polish

## Goal
End-to-end integration pass across all waves. Fix cross-wave issues, optimize performance, ensure consistent error handling, run full lint/typecheck, and update HANDOFF.md with final project state.

## Files to Create/Modify

### 1. Cross-wave integration checks
Verify and fix these integration points:
- **Client → Project → BOQ → Task → Time Entry → Invoice** full lifecycle
- **Auth → RBAC** — all new endpoints (reports, exports) respect role permissions
- **Dashboard → Reports** — dashboard KPI cards link to detailed report pages
- **Reports → Export** — export buttons on report pages trigger correct endpoints

### 2. Performance optimization
Check and fix N+1 queries in:
- `src/backend/db/repositories/project_repo.py` — ensure `selectinload` or `joinedload` for relationships
- `src/backend/services/report_service.py` — batch queries, avoid per-row DB hits
- Add pagination to any list endpoint missing it (check `/api/clients`, `/api/projects`, `/api/reports/client-summary`)
- Add `db.index()` on foreign keys that lack them

### 3. Error handling consistency
Audit all API routers for consistent error responses:
- 400 for bad requests (use `HTTPException(status_code=400, detail="...")`)
- 401 for unauthenticated
- 403 for unauthorized (RBAC)
- 404 for not found
- 422 for validation errors (Pydantic handles this)
- 500 for unexpected errors (FastAPI default handler)
- Ensure all `except` blocks return proper status codes, not generic 500

### 4. Full lint pass
```bash
cd src/backend && make lint  # or ruff check . && black --check .
cd src/frontend && npm run lint
```
Fix ALL lint warnings and errors.

### 5. Full typecheck pass
```bash
cd src/backend && make typecheck  # or mypy .
cd src/frontend && npx tsc --noEmit
```
Fix ALL type errors.

### 6. Test suite
```bash
make test  # full test suite
```
Ensure 100% pass rate. If any tests fail, fix the underlying code (not the test).

### 7. HANDOFF.md
Modify `HANDOFF.md` to document final state:
- All waves shipped and status
- API endpoints inventory (grouped by domain)
- Frontend pages inventory
- Database models inventory
- Known limitations / tech debt
- Next steps for future development

### 8. Update EXECUTION.md
Modify `plan/EXECUTION.md`:
- Mark wave-3 through wave-8 as SHIPPED
- Update dependency graph
- Add changelog entries for waves 3-8

## Files you must NOT touch
- `src/backend/models/` — no new models (only add indexes if missing)
- `src/frontend/src/components/ui/` — do not modify shadcn components
- `.gitignore`, `docker-compose.yml` — no infra changes

## Acceptance criteria
- [ ] `make test` passes 100% (full suite)
- [ ] `make lint` clean (zero warnings)
- [ ] `make typecheck` clean (zero errors) — or `ruff check . && mypy .`
- [ ] No N+1 query warnings in logs during test run
- [ ] HANDOFF.md updated with complete API/page/model inventory
- [ ] EXECUTION.md shows all waves as SHIPPED
- [ ] All export endpoints return valid responses
- [ ] All report endpoints return valid responses
- [ ] Cross-page navigation works (dashboard → reports → export)
- [ ] Error responses follow consistent format across all endpoints

## Test File
No new test file — this task runs existing tests and fixes failures.

## Constraints
- Time budget: 40 min
- Do not add new features — only fix, optimize, and polish
- Do not refactor working code unnecessarily — touch only what's broken
- No new pip/npm dependencies
- Allowed tools: Read, Write, Edit, Bash, Glob, Grep

## Notes
- This is the FINAL wave task — it should be dispatched last after Tasks 01-04 are complete
- If integration issues require changes to other waves' code, make minimal surgical fixes
- HANDOFF.md is critical for session continuity — be thorough
- Document any known limitations (e.g., "CSV export deferred", "Celery workers not yet configured for PDF export")
- The project is "feature complete" after this wave — future work is scale/hardening
