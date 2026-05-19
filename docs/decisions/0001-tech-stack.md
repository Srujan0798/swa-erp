# ADR-0001: Tech Stack Selection

**Date:** 2026-05-19
**Status:** Accepted
**Deciders:** Srujan (project owner) + orchestrator

## Context
Need to pick tech stack for swa-erp at project kickoff. Project 1 (rfq2boq) uses Python; team has Python skills. ERP needs CRUD-heavy API, modern responsive UI, document storage, background jobs.

## Decision

### Backend: Python 3.11 + FastAPI
**Why:**
- Continuity with Project 1's Python skills
- Modern, type-safe, fast
- OpenAPI auto-generated
- Pydantic v2 for I/O validation
- Async-ready for future scale

**Rejected:**
- Django: faster initial CRUD but heavier; the ERP needs API more than admin UI
- Flask: less batteries-included than FastAPI
- Node/NestJS: would force team to context-switch from Project 1

### Database: PostgreSQL 16
**Why:**
- ACID; relational data fits ERP perfectly
- JSONB for flexible audit logs
- Mature; Indian hosting available

**Rejected:**
- MongoDB: ERP data is relational; transactions matter
- SQLite: not for production multi-user

### ORM: SQLAlchemy 2 + Alembic
**Why:**
- Constitution: "ORM-free SQL strings prohibited"
- Declarative style is clean and type-safe
- Alembic handles migrations

**Rejected:**
- Tortoise / Piccolo: less mature ecosystem
- Raw SQL: rejected by constitution

### Frontend: React 18 + Vite + TypeScript strict
**Why:**
- Most-used UI framework; large hiring pool
- Vite: fast dev experience
- TS strict: catches bugs early

**Rejected:**
- Next.js: SSR not needed for internal ERP
- Vue/Svelte: smaller hiring pool in India

### UI library: shadcn/ui + Tailwind
**Why:**
- Composable, not a closed framework
- We own the code (copy-paste components)
- Tailwind utility-first speeds development

**Rejected:**
- Material UI: too opinionated
- Ant Design: heavy bundle

### Server state: TanStack Query
**Why:**
- Standard for React server state
- Excellent caching, refetching, optimistic updates

**Rejected:**
- Redux Toolkit Query: more boilerplate
- SWR: less feature-rich

### Auth: JWT + bcrypt
**Why:**
- Stateless, scales horizontally
- Standard, well-tested libraries
- 1h access + 30d refresh balances security and UX

**Rejected:**
- Session-based: requires sticky sessions or shared store
- OAuth-only: overkill for internal tool

### Background jobs: Celery + Redis
**Why:**
- Standard Python choice; team familiar
- Used in wave-3+ for PDF gen, email send

**Rejected:**
- RQ: less featured
- Custom queue: don't reinvent

### Deploy: Docker Compose first, k8s later
**Why:**
- One-server VPS sufficient for SWA's scale (50 users, 250 projects/year)
- Compose is simpler; can migrate to k8s in wave-8+ if needed

**Rejected:**
- Bare metal: harder to reproduce
- k8s from day 1: complexity not justified yet

## Consequences

### Positive
- Same Python ecosystem as Project 1 — easier hiring + ops
- Type-safe end-to-end (Pydantic ↔ TypeScript)
- Mature, well-documented stack
- Auto-generated API docs (FastAPI OpenAPI)
- Modern dev experience (Vite, shadcn, Tailwind)

### Negative
- Two languages (Python + TS) — more deps to update
- Initial setup more complex than monolith Django
- Need to maintain own auth/RBAC code (not a Django out-of-the-box feature)

### Neutral
- Open-source stack; no vendor lock-in
- Can be self-hosted on commodity VPS

## Follow-up
- ADR-0002 (when needed): caching strategy
- ADR-0003 (when needed): file storage migration to MinIO/S3
- ADR-0004 (later wave): if multi-tenancy is added
