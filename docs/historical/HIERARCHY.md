# Repository Hierarchy

## Top-level map

| Path | Owner | Purpose |
|---|---|---|
| `README.md` | orchestrator | entry point + quick start |
| `CLAUDE.md`, `KIMI.md` | orchestrator | always-loaded kernel (identical content) |
| `AGENTS.md` | orchestrator | agent registry (symlink to CLAUDE.md) |
| `HANDOFF.md` | orchestrator | session/orchestrator switching protocol |
| `HIERARCHY.md` | orchestrator | this file — repo map |
| `HOW_TO_RUN.md` | orchestrator | dual-tier workflow guide |
| `CHANGELOG.md` | orchestrator | version history |
| `CONTRIBUTING.md` | orchestrator | contribution rules |
| `OS_SETUP.md` | orchestrator | operating system setup guide |
| `SUBMISSION_REPORT.md` | orchestrator | submission status report |
| `BACKEND_TEST_AUDIT_REPORT.md` | workers | backend test audit findings |
| `architecture.png` | orchestrator | architecture diagram |
| `plan/` | orchestrator | strategy (3 living docs: PRD, ARCHITECTURE, EXECUTION) |
| `.specify/` | orchestrator | spec-driven contracts (constitution + wave specs) |
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
| `artifacts/` | workers | build/test artifacts |
| `evals/` | workers | evaluation datasets & results |
| `results/` | workers | test/benchmark results |
| `schema/` | workers | JSON/OpenAPI schemas |
| `workflows/` | CI | workflow definitions |
| `uploads/` | runtime | file uploads (see `docs/conventions.md`) |
| `backups/` | orchestrator | automated backups |
| `resources/` | workers | static resources |

**Corrected 2026-07-21**: `data/`, `prompts/`, `config/` were listed here from the
generic project template but were never actually instantiated for this project — none of these
three directories exist in the repo. Runtime uploads actually live in a flat `uploads/` directory
at repo root (see `docs/conventions.md`). Removed from the table above rather than leaving
entries for directories that don't exist.

| `.github/workflows/` | CI | automated checks (ci, test, security) |
| `.claude/` | Claude Code | settings.local.json (minimal) |
| `docker-compose.yml` | orchestrator | base compose (prod-ready) |
| `docker-compose.dev.yml` | orchestrator | development compose overrides |
| `docker-compose.prod.yml` | orchestrator | production compose overrides |
| `Dockerfile` | workers | backend container image |
| `Dockerfile.frontend` | workers | frontend container image |
| `Makefile` | orchestrator | project commands (dev, test, lint, migrate, dispatch, ship) |
| `pyproject.toml` | workers | Python project config (ruff, black, pytest, mypy) |
| `requirements.txt` | workers | Python dependencies |
| `package.json` | workers | Node.js dependencies (managed via frontend) |
| `playwright.config.ts` | workers | Playwright E2E config |
| `prometheus.yml` | orchestrator | Prometheus scrape config |
| `mcp.json` | orchestrator | MCP server config |
| `skills-lock.json` | orchestrator | locked skill versions |
| `skills.manifest.json` | orchestrator | skill manifest |
| `loop_continuous_improvement.sh` | orchestrator | CI improvement loop script |
| `loop_continuous_improvement.log` | orchestrator | CI improvement loop log |
| `run_gates.sh` | orchestrator | gate runner script |
| `SCOPE_GUARD.md` | orchestrator | project scope declaration (IN/OUT/LATER) |
| `test_results.txt` | workers | aggregated test output |

## Directory inventory (all top-level entries)
- `AGENTS.md`
- `BACKEND_TEST_AUDIT_REPORT.md`
- `CHANGELOG.md`
- `CLAUDE.md`
- `CONTRIBUTING.md`
- `Dockerfile`
- `Dockerfile.frontend`
- `HANDOFF.md`
- `HIERARCHY.md`
- `HOW_TO_RUN.md`
- `KIMI.md`
- `Makefile`
- `OS_SETUP.md`
- `README.md`
- `SUBMISSION_REPORT.md`
- `architecture.png`
- `artifacts/`
- `attic/`
- `backups/`
- `deliverables/`
- `docker-compose.dev.yml`
- `docker-compose.prod.yml`
- `docker-compose.yml`
- `docs/`
- `evals/`
- `loop_continuous_improvement.log`
- `loop_continuous_improvement.sh`
- `mcp.json`
- `node_modules/`
- `orchestrator/`
- `plan/`
- `playwright-report/`
- `playwright.config.ts`
- `prometheus.yml`
- `pyproject.toml`
- `requirements.txt`
- `resources/`
- `results/`
- `run_gates.sh`
- `SCOPE_GUARD.md`
- `schema/`
- `scripts/`
- `skills-lock.json`
- `skills.manifest.json`
- `src/`
- `test-results/`
- `test_results.txt`
- `tests/`
- `uploads/`
- `work/`
- `workflows/`

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
└── main.py           # FastAPI app entry
```
**Corrected 2026-07-21**: `workers/` (Celery tasks) was listed here but never built —
`celery==5.4.0` is a listed dependency in `requirements.txt` and mentioned in the tech-stack
line of several docs, but there is no Celery app, no `@task`, and no worker service in either
compose file anywhere in this codebase (confirmed by a full-project audit). It's an unused
dependency, not implemented infrastructure — remove references to a working Celery pipeline
elsewhere in this repo's docs if you find them, or file a real task to build it if background
jobs are actually needed.

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

