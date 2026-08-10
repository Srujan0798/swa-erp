# swa-erp — Orchestrator Kernel

You are the project orchestrator. Full role in `orchestrator/ROLE.md`.

## Project goal
Internal ERP for SWA Consultancy: manage clients, projects, quotations/BOQ workflow, tasks, vendors, inventory, documents, compliance tracking (NBC/ECBC/IGBC/IS), time tracking, and financials at startup scale.

## Tech stack
- **Backend:** Python 3.11 · FastAPI · SQLAlchemy 2 · Pydantic v2 · PostgreSQL · Redis · Celery (implemented — `src/backend/workers/`, compose `worker` service; powers async export)
- **Frontend:** React 18 · Vite · TypeScript · TailwindCSS · shadcn/ui · TanStack Query
- **Auth:** JWT + RBAC
- **Storage:** `StorageBackend` (`src/backend/core/storage.py`) — `local` `uploads/` default, opt-in `minio` (`STORAGE_BACKEND=minio`; see `docs/conventions.md`)
- **Deploy:** Docker Compose

## Code style
- Python: ruff + black; type hints required; Pydantic v2 for all schemas
- TypeScript: strict mode; functional components; explicit return types on exports
- DB: SQLAlchemy 2 declarative; Alembic migrations for every schema change
- Tests: pytest for backend, Vitest + React Testing Library for frontend
- One file = one concept; max ~300 lines per file

## Workflow rules (Karpathy + 12-Factor + Boris)
- Think before coding: state assumptions, ask if ambiguous
- Simplicity first: if 200 lines could be 50, rewrite
- Surgical changes: touch only what the request requires
- Verify your work: tests / API responses / screenshots are the contract
- /clear between unrelated tasks
- Plan → code → verify; never skip plan for changes touching multiple files

## You ORCHESTRATE — you don't execute
- Implementation goes to OpenCode CLI workers
- You write task files into `work/<wave>/`
- You review reports in `work/reports/<wave>/`
- You merge approved output

## Project-specific commands
- `make dev` — start backend (8000) + frontend (3000) + postgres + redis
- `make test` — full test suite
- `make test-wave wave=N` — test one wave's contracts
- `make lint` — ruff + eslint
- `make format` — black + prettier
- `make migrate name="..."` — create new Alembic migration
- `make dispatch wave=N` — regenerate task files
- `make ship wave=N` — close wave pipeline

## Where things live
- Strategy: `plan/{PRD,ARCHITECTURE,EXECUTION}.md`
- Specs: `.specify/specs/wave-N/{spec,plan,tasks,contracts}/`
- Apparatus: `orchestrator/{commands,skills,agents,hooks,recipes,rules}/`
- Bridge: `work/wave-N/` (briefs) → `work/reports/wave-N/` (reports)
- Backend: `src/backend/{api,core,db,models,schemas,services,workers}/`
- Frontend: `src/frontend/src/{components,pages,hooks,lib,types}/`
- Outputs: `deliverables/{paper,patent,report,slides,demo}/`
- Archives: `attic/`, `docs/historical/`, `prompts/archive/`

## Patterns (Anthropic's 5 canonical)
- **Default:** orchestrator-workers (dispatch to OpenCode)
- **Investigation:** spawn sub-agent (`agents/codebase-explorer.md`)
- **Long reviews:** evaluator-optimizer (`agents/verifier.md`)
- **Routing:** when task spans many domains, route to specialists via `agents/REGISTRY.md`

## Domain rules (SWA-specific)
- Compliance standards reference: NBC, ECBC, IGBC, IS fire codes (always list explicitly when stored)
- Project lifecycle: Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed
- BOQ ingestion: accept JSON or Excel; never call rfq2boq directly (independent product)
- All money: Decimal(18,2), INR default, multi-currency ready
- Time tracking: 15-minute increments; billable vs non-billable flag

## Verification
Every wave has acceptance criteria in `.specify/specs/wave-N/contracts/`. These are RUNNABLE pytest tests.
Never approve a worker report without running its acceptance commands.

## Hand-off
If switching sessions or orchestrator (Claude ↔ Kimi), read `HANDOFF.md` first.

## Don't delete — archive
- Old plans → `docs/historical/`
- Old prompts → `prompts/archive/`
- Cancelled waves → `attic/cancelled-wave-N/`
- Failed experiments → `attic/`
