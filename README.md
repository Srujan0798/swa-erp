# SWA ERP

Internal ERP for SWA Consultancy Pvt. Ltd. — an insulation engineering startup (Ahmedabad). The ERP manages clients, projects, quotations/BOQ workflow, tasks, vendors/inventory, documents, compliance, time/financials, and reporting at startup scale.

**Not coupled to rfq2boq.** BOQ files are imported as uploads (JSON/Excel) — the ERP doesn't call the RFQ→BOQ extractor; it consumes outputs of any source.

## Quick start

```bash
git clone <repo>
cd swa-erp
cp .env.example .env
make install
make dev
```

Visit `http://localhost:3000` (frontend) and `http://localhost:8000/docs` (API).

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

**Corrected 2026-08-07.** Celery and MinIO are NOT live. Celery is an installed
dependency (`requirements.txt`) with zero implementation — no app, no `@task`, no worker service;
Redis is used only as a cache. MinIO/S3 is not wired at all; storage is a local `uploads/`
directory. Both remain target-state (see `docs/conventions.md`).

## Deliverables

- Application: `src/backend/` + `src/frontend/`
- Tests: `tests/`
- Technical report: `deliverables/report/`
- Slides: `deliverables/slides/`
- Demo: `deliverables/demo/`

## Company context

SWA Consultancy is an insulation engineering firm (thermal, acoustic, passive fire) serving hospitality, manufacturing, education, and commercial sectors across India. ~750 projects in 3 years. Standards: NBC, ECBC, IGBC, IS fire codes. Products: INSUDESIGN (design + vendor + on-site) and INSUAUDIT.
