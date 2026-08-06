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

- **Backend:** Python 3.11 · FastAPI · SQLAlchemy 2 · Pydantic v2 · PostgreSQL · Celery · Redis
- **Frontend:** React 18 · Vite · TypeScript · TailwindCSS · shadcn/ui · TanStack Query · React Router
- **Auth:** JWT + bcrypt (role-based access control)
- **Storage:** Local filesystem (dev) → MinIO/S3 (prod)
- **Deploy:** Docker Compose

## Deliverables

- Application: `src/backend/` + `src/frontend/`
- Tests: `tests/`
- Technical report: `deliverables/report/`
- Slides: `deliverables/slides/`
- Demo: `deliverables/demo/`

## Company context

SWA Consultancy is an insulation engineering firm (thermal, acoustic, passive fire) serving hospitality, manufacturing, education, and commercial sectors across India. ~750 projects in 3 years. Standards: NBC, ECBC, IGBC, IS fire codes. Products: INSUDESIGN (design + vendor + on-site) and INSUAUDIT.
