# Handoff Protocol

## Why this file exists
Switching orchestrators (Claude ↔ Kimi) or starting a fresh session shouldn't require re-explaining the project. This file lets the new session catch up in < 5 minutes.

## Current state (2026-08-11 — PROJECT COMPLETE: v1.0.1)

- **Status:** Waves 1-31 ✅ SHIPPED, verified, and **pushed to `origin/main`**
  (GitHub `Srujan0798/swa-erp`). Final release **`v1.0.1`** (tagged + pushed), replacing
  `v1.0.0`. Version files (`pyproject.toml`, `src/frontend/package.json`,
  `package-lock.json`) all say **1.0.1**. Working tree clean, no worktrees/branches/stashes.
- **v1.0.1 (wave-31, 2026-08-10) closed the last deferred features:**
  - **Object storage:** `StorageBackend` (`src/backend/core/storage.py`) — `local` `uploads/`
    default (byte-identical to 1.0.0), opt-in `minio` (`STORAGE_BACKEND=minio`, compose `minio`
    service). Files from before wave-31 are not auto-migrated (deployment-time concern).
  - **Celery worker:** `src/backend/workers/` (`celery_app` + `@task`s), compose `worker`
    service, Redis broker/backend; async export via `?async=true` → `202 job_id` + poll
    `GET /api/jobs/{id}`. Sync export path unchanged. Email is the one integration still on the
    request path.
  - Alembic migration graph collapsed from 7 heads → 1 (`c4dd496`).
- **Cleanup sweep (2026-08-11, `0748c7f`):** `backups/` untracked + gitignored (runtime
  output); FileBrowser "New Folder" dialog wired to `useCreateFolder` (was a dead `TODO`).
- **Verification (all run this session against the live stack):** backend suite
  **413 passed / 6 skipped / 0 failed**; `ruff check src/backend/` clean; frontend
  `npm run build` (tsc) clean; wave-31 tests 20 passed / 6 skipped. Historical evidence in
  `work/reports/wave-30/` and `work/reports/wave-31/`.
- **Client submission package:** `deliverables/SUBMISSION.md` (v1.0.1) — what was built,
  verification evidence, explicit drop list, known limitations, deploy pointer, Excel import
  pointer, docs map, and support/next steps.
- **Group chat (2026-08-11):** Srujan already posted the 3 data Qs + 8 server Qs in WhatsApp.
  Viraj answered data Qs; said **there is no IT department** and he's busy but will try server
  answers later. Srujan already said "ok no worries." Do **not** re-send SEND_*.md as if unsent.
- **Viraj data Qs — ANSWERED:** APEX/INNER = clients; INSUDESIGN = service name; yearly ID
   reset everywhere; no Leads sheet. Locked in ADR-0002. **No code change.** Reply sent:
   `deliverables/REPLY_VIRAJ.md` (includes LDI example he asked for).
- **Deploy blocker:** server facts (Docker/WSL/ports/HTTPS/hostname/etc.) — owned by **Viraj**
  (no IT dept), slow path. Until then product stays complete but not company-server live.
- **Where to start:** `MASTER-FLOW.md` → paste reply from `REPLY_VIRAJ.md` → wait / help when
  Viraj has bandwidth for server.

## Where to start a new session
1. Read this file
2. Read `CLAUDE.md` (kernel)
3. Read `plan/EXECUTION.md` (wave status)
4. Read most recent ADR in `docs/decisions/`
5. Run `/status` to see live state

## When you've just merged a wave
Update this file:
- Bump "Active wave" to wave-N+1
- Summarize what shipped
- Note open issues / carry-overs to next wave

## When switching Claude ↔ Kimi
- No file changes needed
- Both read root CLAUDE.md (Kimi treats KIMI.md as alias — identical content)
- Same workflow, same commands
- Auto-memory in `orchestrator/memory/MEMORY.md` is shared

## When onboarding a worker (rare — workers should be stateless)
Workers DON'T read this file. Their task brief in `work/<wave>/` is self-contained.
Workers receive:
1. `work/WORKER_PROMPT.md` (universal prefix)
2. One task file from `work/wave-N/`
That's it. No project memory needed.

## Open decisions (live)
- _None yet — see ADRs in docs/decisions/ as they accumulate_

## Wave roadmap recap
1. Foundation (auth, users, roles, base data model, shell) — ✅ SHIPPED `df1b779`
2. Clients + Projects core (CRM-lite, project CRUD) — ✅ SHIPPED `d1e3017`
3. Quotation/BOQ workflow (upload BOQ, quote versions, approvals) — ✅ SHIPPED `f49eac1`
4. Task management (per-project tasks, assignments, deps) — ✅ SHIPPED (`ed71fac` bulk commit)
5. Vendor + Inventory (vendor DB, materials catalog, RFQ-to-vendor) — ✅ SHIPPED (`ed71fac`)
6. Documents + compliance tracking (NBC/ECBC/IGBC/IS checklist) — ✅ SHIPPED (`ed71fac`)
7. Time tracking + financials (timesheets, invoicing, project P&L) — ✅ SHIPPED (`ed71fac`)
8. Reports + dashboards + deliverables (paper/report/slides/demo) — ✅ SHIPPED `58864df`
9. Core ID chain — Inquiry, Service Agreement, Token, Document Reference — ✅ SHIPPED, closed
   the real client-requested MVP gap (`c3367fa`)
10. Sustainability metrics — ✅ SHIPPED (`a155000`)
11. Reconcile dangling uncommitted frontend work — ✅ SHIPPED (`4e0655d`)
12. Independent verification (real test run, Docker, E2E) — ✅ SHIPPED (`9852ec0`)
13. Excel → ERP data migration importer — ✅ SHIPPED (`466d8ae`)
14. Docker Compose auto-migration + seed fix — ✅ SHIPPED (`ab0a786`)
15. E2E test fixes — ✅ SHIPPED (`4be7536`)
16. Model/migration drift sweep — ✅ SHIPPED (`d5b2790`)
 17-21. Notifications mount, security hardening, backup scripts, prod config templates,
   handover docs — ✅ SHIPPED (see `work/reports/wave-N/` and the status table in
   `plan/EXECUTION.md`)
 22-30. Audit fixes (RBAC, correctness, dead-code/UI), security/lint, doc consolidation, and the
   **v1.0.0 release** — ✅ SHIPPED; see `plan/EXECUTION.md` status table and
   `deliverables/SUBMISSION.md`
 31. Deferred features — MinIO/S3 storage + Celery worker — ✅ SHIPPED (**v1.0.1**, 2026-08-10)

## Key project context
- **Tech stack:** Python 3.11, FastAPI, SQLAlchemy 2, Pydantic v2, PostgreSQL, Redis, React 18, Vite, TS, Tailwind, shadcn/ui, TanStack Query. Celery is implemented (`src/backend/workers/`, compose `worker` service, Redis broker/backend) and powers async export endpoints (`?async=true` → `GET /api/jobs/{id}`). Storage goes through `StorageBackend` (`src/backend/core/storage.py`) — `local` `uploads/` default, opt-in `minio` backend. See `HIERARCHY.md`.
- **Auth:** JWT + RBAC (roles: admin, pm, designer, auditor, viewer)
- **Money:** Decimal(18,2), INR default, multi-currency ready
- **Compliance standards:** NBC, ECBC, IGBC, IS fire codes (explicit references required)
- **Project lifecycle:** Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed
- **BOQ ingestion:** JSON or Excel; never call rfq2boq directly (independent product)
- **Time tracking:** 15-min increments; billable vs non-billable flag
