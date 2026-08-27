# Wave-42 Task 01 — Architecture, schema and flow documentation

T2 additions (§1.5). An evaluator opening this repo needs to understand the system in minutes without reading 152 endpoints.

## Files you own (touch nothing else)
- `docs/architecture/architecture.mmd` + `docs/architecture/*.md`
- `architecture.png` (generated from the .mmd)
- `docs/schemas/` (ERD + OpenAPI export)
- `docs/flows/`
- `docs/REPOSITORY_STRUCTURE_AND_CLEANUP_PLAN.md`
- `schema/db_struct.sql`

## Ground truth (verify before drawing — do NOT guess)
- 26 API routers, 152 endpoints, 25 models, 30 migrations, 26 frontend pages, 19 hooks.
- The client's real business chain, which is the intellectual core of this project:
  `Inquiry → Client → Service Agreement → Token → Document Reference → Time Log → Sustainability`
  Reference IDs are `SWA-{year}-{TYPE}-{seq:03d}`, generated atomically by `src/backend/services/reference_id_service.py`.
- Storage is a `StorageBackend` protocol (`src/backend/core/storage.py`): local `uploads/` default, opt-in MinIO. Celery workers are real (`src/backend/workers/`).
- Mark **built vs target-state explicitly**. This repo has a documented history of diagrams implying things existed when they didn't — do not regress that.

## The work
1. **`architecture.mmd`** — system context, the core-chain data model, request lifecycle, deployment topology. Must render on GitHub. Generate `architecture.png` (`mmdc -i ... -o ...`, or document the exact command if mermaid-cli is unavailable).
2. **`docs/schemas/`** — ERD of the 25 models (mermaid `erDiagram`), and export the live OpenAPI spec from the running app (`/openapi.json`) to `docs/schemas/api.yaml`. Export it, don't transcribe it.
3. **`docs/flows/`** — one document per critical flow with a diagram + prose: the core ID chain end-to-end, auth/RBAC, BOQ→quote→invoice, async export via Celery.
4. **`docs/REPOSITORY_STRUCTURE_AND_CLEANUP_PLAN.md`** — per §4.14. Count real files. Include drift indicators: files referenced in `CLAUDE.md`/`HIERARCHY.md` that don't exist, and files in `src/` nothing imports. Note: `orchestrator/agents/deep-research.md` is a known orphan (nothing references it).
5. **`schema/db_struct.sql`** — dump the real schema (`pg_dump --schema-only`) from a migrated database. Do not hand-write it.

## Acceptance criteria
- [ ] Every mermaid block renders — verify, don't assume; paste how you verified
- [ ] `architecture.png` exists and matches the `.mmd` source
- [ ] `docs/schemas/api.yaml` was exported from a running app, not transcribed — say which command produced it
- [ ] `schema/db_struct.sql` came from `pg_dump` — paste the command
- [ ] Built vs target-state marked on every diagram
- [ ] Endpoint/model/page counts match what you actually measured

## Deliver
`work/reports/wave-42/01-architecture-schema-docs.report.md`. Commit before writing it.

## Constraints
- Time budget: 150 min · commit per artifact
- Zero application-code changes
