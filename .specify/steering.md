# Steering — Custom AI Rules for SWA ERP

## When deciding tech for a new feature
1. Default to **stack-aligned** choices (FastAPI + SQLAlchemy + React + TanStack Query).
2. If a new library is required, write an ADR in `docs/decisions/`.
3. Prefer **boring tech** over novel tech. Postgres > Mongo. JWT > OAuth-server. Celery > custom queue.

## When writing code
- Backend services accept Pydantic schemas, never `dict`.
- Database mutations go through repositories, never `Session.execute(raw sql)`.
- API responses always include `request_id` (from middleware) for debugging.
- Errors are typed: `ClientError` (4xx), `ServerError` (5xx), `IntegrationError` (external services).

## When designing UIs
- Use shadcn/ui components first; only build custom when shadcn doesn't cover.
- TanStack Query for all server state; React Context only for auth/theme.
- Forms via react-hook-form + zod resolver.
- Loading states everywhere; never a blank screen.
- Empty states are first-class designs, not afterthoughts.

## When writing tests
- Unit tests for services (business logic).
- Integration tests for API routes (with real DB via test transactions).
- E2E tests for critical user flows (login → create project → upload BOQ → quote sent).
- Golden tests for BOQ parsers (fixed input → fixed output, breaks if parser drifts).
- Performance tests for list endpoints under realistic load (100 clients, 1000 projects).

## When the orchestrator picks workers
- Backend tasks → Python-strong worker (OpenCode CLI with python skill bundle)
- Frontend tasks → TS-strong worker
- DB migrations → backend worker with explicit Alembic skill
- Parser tasks (BOQ Excel) → worker with `pdf-processing` or `excel-processing` skill from agentskills.io

## Standards versioning
When a wave touches compliance:
- Add `standard_version` field to the relevant table (e.g., `nbc_version = "2024"`)
- Never delete old standard rows; mark inactive
- Migration that adds new standards is a non-breaking ADD operation
