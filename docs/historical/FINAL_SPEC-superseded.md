# FINAL_SPEC — SWA-ERP

> **Date**: 2026-07-01
> **Tests**: 97/97 passing
> **Sessions**: 123 processed (4 deleted, 119 categorized)

---

## §0. CURRENT STATE

- **Running PIDs**: None (no background experiments)
- **Test status**: 97/97 passing (0 failures)
- **Code freeze**: Backend complete, frontend routing fixed
- **OpenCode DB**: 5.0GB (123 sessions)
- **Uncommitted changes**: 15 modified + ~100 new files (waves 3-8)

---

## §1. IMMEDIATE — DO NOT TOUCH

- `tests/conftest.py` — Test fixtures, DB setup
- `src/backend/main.py` — App entry point, all routers mounted
- `src/backend/alembic/` — Migration files (14 migrations)
- All passing test files — Do not modify without running full suite

---

## §2. AFTER THIS SESSION — EXACT COMMAND SEQUENCE

```bash
# Step 1: Run tests to verify everything still passes
python3 -m pytest tests/ -q

# Step 2: Stage all wave 3-8 code
git add src/backend/models/ src/backend/api/ src/backend/services/
git add src/backend/schemas/ src/backend/db/repositories/
git add src/backend/alembic/versions/
git add src/frontend/src/pages/ src/frontend/src/components/
git add src/frontend/src/hooks/ src/frontend/src/types/

# Step 3: Commit wave 3-8 backend + frontend
git commit -m "feat(waves 3-8): complete BOQ, tasks, vendors, docs, compliance, time, financials, reports"

# Step 4: Stage test fixes
git add tests/
git commit -m "test: fix wave-6 compliance and wave-8 reports — 97/97 passing"

# Step 5: Stage routing fixes
git add src/frontend/src/App.tsx src/frontend/src/components/layout/Sidebar.tsx
git commit -m "fix: add missing frontend routes for vendors, compliance, documents"

# Step 6: Stage export service fix
git add src/backend/services/export_service.py
git commit -m "fix: export_service dict attribute access in demo_package"

# Step 7: Stage handoff docs
git add ULTIMATE_HANDOFF.md FINAL_SPEC.md
git commit -m "docs: KleenHand cleanup — ultimate handoff + final spec"

# Step 8: Push
git push origin main
```

---

## §3. STALE CONTENT TO FIX

| File | Issue | Fix |
|------|-------|-----|
| App.tsx | Missing routes for tasks, quotes, BOQs, invoices, time, reports | Add routes (pages exist but not wired) |
| Sidebar.tsx | Missing nav items for tasks, quotes, time, financials, reports | Add nav items |

---

## §4. BLOCKED ITEMS

| Blocker | Why | Unblock Strategy |
|---------|-----|------------------|
| Waves 3-8 not committed | Code exists but never git committed | Run commit strategy above |
| Frontend E2E tests not run | Playwright config exists, tests written | Run `npx playwright test` |
| Docker not verified | Dockerfile exists | Run `docker compose up` |

---

## §5. FINAL DELIVERABLES CHECKLIST

- [x] Backend models — 18 domain models
- [x] Backend APIs — 20+ routers
- [x] Backend services — 22 service files
- [x] Backend schemas — 19 Pydantic v2 schemas
- [x] Backend repositories — 19 DB access layers
- [x] Alembic migrations — 14 migration files
- [x] Frontend pages — 14 pages
- [x] Frontend components — 52+ components
- [x] Frontend hooks — 10+ TanStack Query hooks
- [x] Frontend routing — Core routes fixed
- [x] Sidebar navigation — Core nav items added
- [x] Backend tests — 97/97 passing
- [x] RBAC — 5 roles implemented
- [x] Compliance — NBC/ECBC/IGBC/IS standards
- [x] Exports — PDF, JSON export service
- [ ] Waves 3-8 committed to git
- [ ] Frontend routes for tasks/quotes/BOQs/invoices/time/reports
- [ ] Frontend E2E tests verified
- [ ] Docker deployment verified

---

## §6. COMMIT STRATEGY

See §2 for exact commands. Five commits in sequence:
1. `feat(waves 3-8)` — All backend + frontend code
2. `test:` — Test fixes
3. `fix:` — Routing fixes
4. `fix:` — Export service bugfix
5. `docs:` — KleenHand cleanup docs

---

## §7. NARRATIVE SUMMARY

SWA-ERP is a full-stack ERP system for SWA Consultancy built across 15 waves. The backend implements 18 domain models, 20+ API routers, and 22 service files with complete business logic. The frontend has 14 pages and 52+ components. All 97 backend tests pass after fixing wave-6 compliance tests (DB dependency override, URL mismatches, role-based auth) and wave-8 reports tests (schema mismatches, ForeignKeyViolation). The critical remaining work is committing waves 3-8 to git and wiring up remaining frontend routes.

---

*FINAL_SPEC v1 — 2026-07-01*
*97/97 tests passing*
*KleenHand cleanup complete*
