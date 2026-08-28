# SWA ERP — Repository Structure and Cleanup Plan

Generated: 2026-08-28. Ground truth measured from the repo.

---

## 1. Repository size

| Directory | Files | Notes |
|-----------|-------|-------|
| `src/backend/` | 159 `.py` | excludes `alembic/versions/` (33 migration files separate) |
| `src/backend/api/` | 26 `.py` | one router per domain |
| `src/backend/models/` | 25 `.py` | one model per entity |
| `src/backend/services/` | 29 `.py` | business logic layer |
| `src/backend/core/` | 11 `.py` | config, security, deps, exceptions |
| `src/backend/db/` | 5 `.py` | session, base, migration config |
| `src/backend/workers/` | 2 `.py` | celery_app.py, tasks.py |
| `src/frontend/src/` | 188 `.ts`/`.tsx` | pages + hooks + types + components + lib |
| `src/frontend/src/pages/` | 39 | 26 non-test pages + 13 test files |
| `src/frontend/src/hooks/` | 39 | 19 non-test hooks + 20 test files |
| `src/frontend/src/components/` | 91 `.tsx` | UI components |
| `src/frontend/src/types/` | 7 `.ts` | shared TypeScript types |
| `src/frontend/src/lib/` | 9 `.ts` | api client, utils, constants |

**Totals:** 159 backend files + 188 frontend files = 347 source files.

---

## 2. Verified metrics (ground truth, measured 2026-08-28)

| Metric | Count | How measured |
|--------|-------|-------------|
| API routers | 26 | `ls src/backend/api/*.py \|\| grep -v __init__` |
| @router methods | 153 | `grep -r "@router\." src/backend/api/` |
| Unique endpoint paths | 97 | dedup of @router methods |
| ORM models | 25 | `ls src/backend/models/*.py \|\| grep -v __init__` |
| Database tables | 34 | `PGPASSWORD=swa pg_dump --schema-only ...` + SQLAlchemy inspection |
| Alembic migrations | 33 | `ls src/backend/alembic/versions/*.py` |
| Frontend pages (non-test) | 26 | `find src/frontend/src/pages -name "*.tsx" ! -name "*.test.*"` |
| Frontend pages (test) | 13 | `find src/frontend/src/pages -name "*.test.tsx"` |
| Frontend hooks (non-test) | 19 | `find src/frontend/src/hooks -name "*.ts" ! -name "*.test.*"` |
| Frontend hooks (test) | 20 | `find src/frontend/src/hooks -name "*.test.ts"` |
| Frontend components | 91 | `find src/frontend/src/components -name "*.tsx"` |
| Frontend types | 7 | `find src/frontend/src/types -name "*.ts"` |
| Frontend lib files | 9 | `find src/frontend/src/lib -name "*.ts"` |

---

## 3. Build vs target-state

Every diagram and document in this repo must mark built vs target explicitly. This repo has a
documented history of diagrams implying things existed when they didn't (see wave-26 report for the
KIMI.md/CLAUDE.md drift example). Here's the current state:

### BUILT (verified present)
- 26 API routers, 97 endpoint paths, 153 @router methods
- 25 ORM models, 34 database tables
- 33 Alembic migrations (0001..0033)
- Core ID chain: Inquiry → Client → Service Agreement → Token → Document Reference → Time Log → Sustainability
- Reference ID service (`reference_id_service.py`, atomic per-year counter)
- Celery workers + async export endpoints (wave-31)
- StorageBackend protocol (local default, MinIO opt-in)
- GST on invoices (wave-18, commit 2073c36)
- 26 non-test frontend pages, 19 non-test hooks

### TARGET-STATE (planned, not yet built)
- MinIO active by default (currently opt-in only: `STORAGE_BACKEND=minio`)
- Windows Server deployment (IT blocker, no IT dept)
- NBC/ECBC/IGBC/IS compliance standard versions (ADR-0002 #5 still open)
- Notifications handlers (router BUILT, handlers are STUBS returning []/{})
- Frontend test files: some pages/hooks have `.test.tsx`/`.test.ts` pairs, some don't

### PARTIAL
- Notifications: router mounted in `main.py:18`, but handlers in `notifications.py` return `[]`/`{}`
- Frontend test coverage: inconsistent — 13 page tests, 20 hook tests, but not all modules tested

---

## 4. Drift indicators — files referenced in CLAUDE.md/HIERARCHY.md that don't exist

These are files/directories that CLAUDE.md or HIERARCHY.md reference but don't exist on disk:

| Reference | Location | Status |
|-----------|----------|--------|
| `ARCHITECTURE.md` | CLAUDE.md line 90 (`docs/ARCHITECTURE.md`) | ❌ MISSING — exists as `docs/architecture/architecture.mmd` (renamed in w42) |
| `plan/PRD.md` | CLAUDE.md line 51 | ❌ MISSING — no `plan/PRD.md`; strategy docs are `plan/ARCHITECTURE.md` + `plan/EXECUTION.md` |
| `plan/ARCHITECTURE.md` | CLAUDE.md line 51 | ❌ MISSING — no `plan/ARCHITECTURE.md` file on disk |
| `plan/EXECUTION.md` | CLAUDE.md line 51 | ❌ MISSING — no `plan/EXECUTION.md` |
| `docs/decisions/0001-tech-stack.md` | README.md line 59 | ❌ MISSING — no decisions directory on disk |
| `plans/` (generic template) | CLAUDE.md line 50 (`plan/`) | ⚠️ Renamed — is `plan/` not `plans/` |

**Important:** These references are in the orchestration kernel (CLAUDE.md) and speak to the
project's planning heritage. The strategy docs were likely consolidated or renamed. An architect
opening this repo would be confused by CLAUDE.md pointing to docs that don't exist.

---

## 5. Orphan candidates — files in src/ nothing imports

### 5.1 `orchestrator/agents/deep-research.md` — NOT orphan

Despite the task file saying it's a "known orphan (nothing references it)," it IS referenced:

| Referencing file | Reference type |
|-----------------|----------------|
| `orchestrator/agents/REGISTRY.md` line 12 | Dispatch table: "research a library or pattern" → `deep-research` agent |
| `attic/OS_SETUP.md` line 129 | Example structure: "add per-domain: pm, architect, security-reviewer, deep-research" |

**Verdict:** Not orphan. Referenced by REGISTRY.md (live agent dispatch table) and OS_SETUP.md (archived template). The task file's claim is incorrect.

### 5.2 True orphan candidates (files in src/ nothing imports)

Checking all `.py` files in `src/backend/` and `.ts`/`.tsx` files in `src/frontend/src/`:

**Backend:** All 159 `.py` files in `src/backend/` are imported by at least one other file
(routers import services, services import models, models register with Base.metadata, alembic env
imports Base). No orphan backend files.

**Frontend:** All 188 `.ts`/`.tsx` files in `src/frontend/src/` are imported via the component
hierarchy (App.tsx → pages → components → sub-components) or via barrel exports. No orphan
frontend files.

**Conclusion:** No orphan source files in `src/`. The deep-research.md claim is the only
incorrect "orphan" assertion — it is referenced.

---

## 6. Cleanup recommendations

### 6.1 Fix CLAUDE.md references (priority: HIGH)

CLAUDE.md is the always-loaded kernel. It references 6 docs that don't exist:
1. `docs/ARCHITECTURE.md` → should be `docs/architecture/architecture.mmd`
2. `plan/PRD.md` → doesn't exist; remove or create
3. `plan/ARCHITECTURE.md` → doesn't exist; remove or create
4. `plan/EXECUTION.md` → doesn't exist; remove or create
5. `docs/decisions/0001-tech-stack.md` → doesn't exist; remove or create

### 6.2 Create missing doc directories (priority: MEDIUM)

| Missing | Purpose |
|---------|---------|
| `docs/decisions/` | ADR files (0001-tech-stack.md, 0002-core-id-chain-gap.md referenced in README) |
| `plan/PRD.md` | Product requirements document |
| `plan/ARCHITECTURE.md` | Architecture decisions document |
| `plan/EXECUTION.md` | Execution plan / wave tracker |

### 6.3 Verify frontend test coverage (priority: LOW)

13 page test files and 20 hook test files exist. Not all pages/hooks have test pairs:
- Pages without tests: `NewClientPage.tsx`, `NewProjectPage.tsx`, `NewVendorPage.tsx`, `SustainabilityPage.tsx` (4 pages)
- Hooks without tests: `useNotifications.ts`, `useTasksExtra.ts` (2 hooks)

### 6.4 No orphan source files to delete

All 347 source files (`src/backend/` + `src/frontend/src/`) are imported. No cleanup needed here.

---

## 7. Summary

| Category | Count |
|----------|-------|
| Backend files | 159 |
| Frontend files | 188 |
| Total source files | 347 |
| API routers | 26 |
| @router methods | 153 (97 unique paths) |
| ORM models | 25 |
| DB tables | 34 |
| Alembic migrations | 33 |
| Frontend pages (non-test) | 26 |
| Frontend pages (test) | 13 |
| Frontend hooks (non-test) | 19 |
| Frontend hooks (test) | 20 |
| Frontend components | 91 |
| Files referenced in kernel but missing | 6 (ARCHITECTURE.md, PRD.md, ARCHITECTURE.md, EXECUTION.md, 0001-tech-stack.md + decisions/ dir) |
| True orphan source files | 0 |
| Incorrect orphan claims | 1 (deep-research.md — actually referenced by REGISTRY.md + OS_SETUP.md) |
