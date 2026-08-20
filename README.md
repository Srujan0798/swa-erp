# SWA ERP

> **Role:** Front door / entry point. Every other top-level doc is one table away — see
> "Where to look" below.

Internal ERP for SWA Consultancy Pvt. Ltd. — an insulation engineering startup (Ahmedabad). The ERP manages clients, projects, quotations/BOQ workflow, tasks, vendors/inventory, documents, compliance, time/financials, and reporting at startup scale.

**Not coupled to rfq2boq.** BOQ files are imported as uploads (JSON/Excel) — the ERP doesn't call the RFQ→BOQ extractor; it consumes outputs of any source.

## Where to look

Nine top-level docs compete for your attention. This table says which one to open — you should
never have to guess:

| File | Who it's for | When to read it |
|---|---|---|
| [`README.md`](README.md) | everyone | **first** — you're here |
| [`MASTER-FLOW.md`](MASTER-FLOW.md) | orchestrator + anyone lost | when you need "what to do next" as one line |
| [`CLAUDE.md`](CLAUDE.md) / [`KIMI.md`](KIMI.md) | orchestrator agents | auto-loaded every session (same file) |
| [`HANDOFF.md`](HANDOFF.md) | orchestrators | when a new session or orchestrator takes over |
| [`HIERARCHY.md`](HIERARCHY.md) | everyone | when you need the repo map / where things live |
| [`HOW_TO_RUN.md`](HOW_TO_RUN.md) | anyone running the project | before `make dev` or dispatching work |
| [`CHANGELOG.md`](CHANGELOG.md) | everyone | for version history and release notes |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | contributors / workers | before contributing or writing a brief |

Beyond these, `docs/` holds the reference docs (deployment, runbook, conventions, decisions,
performance, observability) and `plan/` the strategy. Each of the nine files above carries a
one-line role header linking back here.

## Quick start

```bash
git clone <repo>
cd swa-erp
cp .env.example .env
make install
make dev
```

Visit `http://localhost:3100` (frontend) and `http://localhost:8100/docs` (API).  
(Ports **3100 / 8100** — not 3000/8000 — so SWA does not clash with other local apps.)

## How this project is built

Two-tier agentic workflow (per the project's methodology docs in `orchestrator/core/` and
`HOW_TO_RUN.md`):

- **Orchestrator** = Claude Code or Kimi (interchangeable). Plans, dispatches, reviews, merges.
- **Workers** = OpenCode CLI in parallel windows. Execute self-contained task briefs.

See [`HOW_TO_RUN.md`](HOW_TO_RUN.md) for the full workflow.

## Repository map

See [`HIERARCHY.md`](HIERARCHY.md).

## Status

See [`plan/EXECUTION.md`](plan/EXECUTION.md) for wave progress.

## Tech stack

- **Backend:** Python 3.11 · FastAPI · SQLAlchemy 2 · Pydantic v2 · PostgreSQL · Redis
- **Frontend:** React 18 · Vite · TypeScript · TailwindCSS · shadcn/ui · TanStack Query · React Router
- **Auth:** JWT + bcrypt (role-based access control)
- **Storage:** Local filesystem only — all uploads live in `uploads/` at the repo root
- **Deploy:** Docker Compose

**Corrected 2026-08-09.** Storage and background jobs are live. MinIO/S3 is wired via a storage
abstraction (`src/backend/core/storage.py`, `STORAGE_BACKEND=local|minio`, compose `minio`
service; default `local` keeps the historical `uploads/` layout). Celery is implemented
(`src/backend/workers/` app + `@task`s, compose `worker` service, Redis broker/backend) and powers
the async export endpoints (`?async=true` + `GET /api/jobs/{id}`). See `docs/runbook.md`.

## Deliverables

- Application: `src/backend/` + `src/frontend/`
- Tests: `tests/`
- Technical report: `deliverables/report/`
- Slides: `deliverables/slides/`
- Demo: `deliverables/demo/`

## Company context

SWA Consultancy is an insulation engineering firm (thermal, acoustic, passive fire) serving hospitality, manufacturing, education, and commercial sectors across India. ~750 projects in 3 years. Standards: NBC, ECBC, IGBC, IS fire codes. Products: INSUDESIGN (design + vendor + on-site) and INSUAUDIT.
