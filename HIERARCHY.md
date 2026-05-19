# Repository Hierarchy

## Top-level map

| Path | Owner | Purpose |
|---|---|---|
| `README.md` | orchestrator | entry point + quick start |
| `CLAUDE.md`, `KIMI.md` | orchestrator | always-loaded kernel (identical content) |
| `HANDOFF.md` | orchestrator | session/orchestrator switching protocol |
| `HIERARCHY.md` | orchestrator | this file — repo map |
| `HOW_TO_RUN.md` | orchestrator | dual-tier workflow guide |
| `CHANGELOG.md` | orchestrator | version history |
| `CONTRIBUTING.md` | orchestrator | contribution rules |
| `OS_SETUP.md` | orchestrator | methodology reference (copy from ~/Desktop/OS_SETUP.md) |
| `plan/` | orchestrator | strategy (3 living docs: PRD, ARCHITECTURE, EXECUTION) |
| `.specify/` | orchestrator | spec-driven contracts (constitution + wave specs) |
| `orchestrator/` | orchestrator | commands, skills, agents, hooks, recipes, rules |
| `work/` | orchestrator (write) / workers (read) | task bridge |
| `work/reports/` | workers (write) / orchestrator (read) | report bridge |
| `src/backend/` | workers | FastAPI backend (api, core, db, models, schemas, services, workers) |
| `src/frontend/` | workers | React + Vite frontend |
| `tests/` | workers | unit/integration/e2e/golden/fuzz/performance/security |
| `data/` | workers + scripts | seed data, fixtures, sample uploads |
| `deliverables/` | orchestrator + workers | paper, patent, report, slides, demo |
| `docs/` | orchestrator | reference + decisions + runbook + conventions |
| `prompts/` | orchestrator | evolving worker prompt history (current/archive) |
| `attic/` | nobody (frozen) | superseded work, never deleted |
| `scripts/` | workers + orchestrator | automation utilities |
| `config/` | workers | runtime config |
| `schema/` | workers | JSON Schema / Pydantic definitions |
| `.github/workflows/` | CI | automated checks (ci, test, security) |
| `.claude/` | Claude Code | settings.local.json (minimal) |

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
├── workers/          # Celery tasks
└── main.py           # FastAPI app entry
```

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
