# Repository Hierarchy

## Top-level map

| Path | Owner | Purpose |
|---|---|---|
| `README.md` | orchestrator | entry point + quick start |
| `MASTER-FLOW.md` | orchestrator | the single-path answer: what to do, ask, continue |
| `CLAUDE.md`, `KIMI.md` | orchestrator | always-loaded kernel (identical content) |
| `HANDOFF.md` | orchestrator | session/orchestrator switching protocol |
| `HIERARCHY.md` | orchestrator | this file — repo map |
| `HOW_TO_RUN.md` | orchestrator | dual-tier workflow guide |
| `CHANGELOG.md` | orchestrator | version history |
| `CONTRIBUTING.md` | orchestrator | contribution rules |
| `plan/` | orchestrator | strategy (3 living docs: PRD, ARCHITECTURE, EXECUTION) |
| `.specify/` | orchestrator | constitution only — wave specs archived to `docs/historical/specify-specs/` |
| `orchestrator/` | orchestrator | commands, skills, agents, hooks, recipes, rules |
| `work/` | orchestrator (write) / workers (read) | task bridge |
| `work/reports/` | workers (write) / orchestrator (read) | report bridge |
| `src/backend/` | workers | FastAPI backend (api, core, db, models, schemas, services, workers) |
| `src/frontend/` | workers | React + Vite frontend |
| `tests/` | workers | unit/integration/e2e/golden/fuzz/performance/security |
| `deliverables/` | orchestrator + workers | admin/user guides, architecture summary — built wave-21 |
| `docs/` | orchestrator | reference + decisions + runbook + conventions |
| `attic/` | nobody (frozen) | superseded work, never deleted |
| `scripts/` | workers + orchestrator | automation utilities (import tool, backup scripts) |

**Corrected 2026-07-21**: `data/`, `prompts/`, `config/`, and `schema/` were listed here from the
generic project template but were never actually instantiated for this project — none of these
four directories exist in the repo. Runtime uploads actually live in a flat `uploads/` directory
at repo root (see `docs/conventions.md`). Removed from the table above rather than leaving
entries for directories that don't exist.
| `.github/workflows/` | CI | automated checks (ci, test, security) |
| `.claude/` | Claude Code | settings.local.json (minimal) |

## Directory inventory (all top-level entries)
- `CHANGELOG.md`
- `CLAUDE.md`
- `CONTRIBUTING.md`
- `Dockerfile`
- `Dockerfile.frontend`
- `HANDOFF.md`
- `HIERARCHY.md`
- `HOW_TO_RUN.md`
- `KIMI.md`
- `MASTER-FLOW.md`
- `Makefile`
- `README.md`
- `attic/`
- `backups/`
- `deliverables/`
- `docker-compose.prod.yml`
- `docker-compose.yml`
- `docs/`
- `mcp.json`
- `node_modules/`
- `orchestrator/`
- `plan/`
- `playwright-report/`
- `playwright.config.ts`
- `pyproject.toml`
- `requirements.txt`
- `resources/`
- `scripts/`
- `src/`
- `test-results/`
- `tests/`
- `uploads/`
- `work/`
- `load-test-report-20260819-200408.html`
- `load-test-report-20260819-201658.html`
- `load-test-results-20260819-200408_stats.csv`
- `load-test-results-20260819-200408_stats_history.csv`
- `load-test-results-20260819-200408_failures.csv`
- `load-test-results-20260819-200408_exceptions.csv`
- `load-test-results-20260819-200957_stats.csv`
- `load-test-results-20260819-200957_stats_history.csv`
- `load-test-results-20260819-200957_failures.csv`
- `load-test-results-20260819-200957_exceptions.csv`
- `load-test-results-20260819-201658_stats.csv`
- `load-test-results-20260819-201658_stats_history.csv`
- `load-test-results-20260819-201658_failures.csv`
- `load-test-results-20260819-201658_exceptions.csv`
- `load-test-report-20260819-201906.html`
- `load-test-results-20260819-201906_stats.csv`
- `load-test-results-20260819-201906_stats_history.csv`
- `load-test-results-20260819-201906_failures.csv`
- `load-test-results-20260819-201906_exceptions.csv`
- `load-test-results-20260819-202227_stats.csv`
- `load-test-results-20260819-202227_stats_history.csv`
- `load-test-results-20260819-202227_failures.csv`
- `load-test-results-20260819-202227_exceptions.csv`
- `load-test-report-20260819-202748.html`
- `load-test-results-20260819-202748_stats.csv`
- `load-test-results-20260819-202748_stats_history.csv`
- `load-test-results-20260819-202748_failures.csv`
- `load-test-results-20260819-202748_exceptions.csv`
- `load-test-report-20260819-202748.html`
- `load-test-results-20260819-202748_stats.csv`
- `load-test-results-20260819-202748_stats_history.csv`
- `load-test-results-20260819-202748_failures.csv`
- `load-test-results-20260819-202748_exceptions.csv`

## Wave numbering
Waves are sequential: wave-1, wave-2, ... Don't skip numbers. Cancelled waves → `attic/cancelled-wave-N/`.

## Naming conventions
- Folders: kebab-case (`wave-1/`, `client-portal/`)
- Python files: snake_case (`project_service.py`)
- TypeScript files: PascalCase for components (`ProjectCard.tsx`), camelCase otherwise (`useProjects.ts`)
- Markdown: kebab-case for docs (`scope-guard.md`), SCREAMING_CASE for top-level (`README`, `CLAUDE`, `HANDOFF`)
- Skills, commands, agents: kebab-case matching the directory

## Backend module layout
```
src/backend/
├── api/              # FastAPI routers (one file per domain: clients.py, projects.py, ...)
├── core/             # config, security, deps, exceptions, logging
├── db/               # session, base, migrations (Alembic)
├── models/           # SQLAlchemy ORM models
├── schemas/          # Pydantic request/response models
├── services/         # business logic (no FastAPI deps)
├── workers/          # Celery app + background tasks (PDF/report generation)
└── main.py           # FastAPI app entry
```
**Corrected 2026-08-09 (wave-31 task 02)**: `workers/` is now real — `workers/celery_app.py`
defines the Celery app (Redis broker/backend), `workers/tasks.py` has `@task`s for project-summary
and financial-report PDF generation, and `docker-compose.yml` has a `worker` service running
`celery -A src.backend.workers.celery_app worker`. Async export endpoints (`?async=true`) enqueue
jobs tracked via `api/jobs.py`; results are written through the storage abstraction.

## Frontend module layout
```
src/frontend/src/
├── components/       # reusable UI (one folder per component group)
├── pages/            # route-level views
├── hooks/            # custom hooks (TanStack Query wrappers, etc.)
├── lib/              # api client, utils, constants
├── types/            # shared TypeScript types
├── App.tsx           # route definitions
└── main.tsx          # entry
```

## What goes in attic/
- Old plans superseded by new architecture decisions
- Failed experiments (kept for "we tried this and it didn't work because...")
- Prompt versions from earlier waves
- Anything that's no longer in the live flow but worth referencing
- Cancelled waves → `attic/cancelled-wave-N/`
