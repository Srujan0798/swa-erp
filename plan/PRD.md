# PRD — SWA ERP

## Objective
Build an internal ERP system for SWA Consultancy Pvt. Ltd. (Ahmedabad-based insulation engineering startup) that manages the full operational lifecycle of insulation design/audit projects from lead intake through closeout, supporting startup-scale growth (~250 active projects/year and growing).

## User / Problem
**Primary user:** SWA's 20–50 internal team (PMs, designers, auditors, admins, founders).
**Secondary user:** SWA's clients (read-only project portal in a later wave).

**Problem:** SWA's project volume is growing fast (~750 projects in 3 years). Without a unified system, project data lives in spreadsheets, email threads, and team members' heads. As Project 1 (rfq2boq) accelerates bid intake, downstream operations become the bottleneck: tracking which projects are at which stage, who's assigned to what, what materials are needed, what compliance was checked, what hours were billed, how much was invoiced, and which projects are profitable.

## Scope

**Corrected 2026-07-21** — this section originally called waves 1-4 "MVP," which predates the
discovery (documented in `docs/decisions/0002-core-id-chain-gap.md`) that the client's actual
requested MVP is the Inquiry→Agreement→Token→DocumentReference chain, not the generic CRM built
in waves 1-8. `docs/SCOPE_GUARD.md` was already corrected to reflect this; this file wasn't,
creating a contradiction between two current docs. See `docs/SCOPE_GUARD.md` for the live,
authoritative scope list — this section is kept only as a historical record of the original plan.

### Original plan (waves 1-4, as first scoped — see docs/SCOPE_GUARD.md for what's actually true now)
1. **Auth + RBAC** — admin, PM, designer, auditor, vendor (later), client (later)
2. **Client database** — accounts, contacts, project history per client
3. **Project tracking** — lifecycle (Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed), milestones, status
4. **Quotation/BOQ workflow** — upload BOQ (JSON/Excel from any source), versions, approvals, send to client
5. **Task management** — per-project tasks, assignees, deps, status, due dates

### Original plan (waves 5-8, as first scoped)
6. **Vendor management + Inventory** — vendor DB, materials catalog, RFQ-to-vendor, comparisons
7. **Documents + compliance** — drawings/specs upload, NBC/ECBC/IGBC/IS fire code checklists per project
8. **Time tracking + financials** — timesheets, billable/non-billable, invoicing, payments, project P&L
9. **Reports + dashboards** — utilization, project health, revenue forecast, compliance status

### What actually turned out to be the client-requested MVP (waves 9-10)
Inquiry → Client → Service Agreement → Token → Document Reference → Time Log, plus post-project
Sustainability metrics — see `resources/MEETINGS_MASTER.md` for the full requirement and
`docs/SCOPE_GUARD.md` for current status.

## Non-goals
- **Not a CAD tool.** No drawing creation; only document storage + annotations.
- **Not a BIM platform.** No 3D models, no IFC integration in MVP.
- **Not coupled to rfq2boq.** BOQ files come in as uploads from any source.
- **Not multi-tenant initially.** Single SWA installation; multi-tenancy is a future wave.
- **Not a CRM replacement** for sales-heavy companies; client management is operational-grade (project-centric), not sales-funnel-centric.
- **Not an accounting system.** Generates invoices but doesn't replace Tally/Zoho Books; exports for accountants.
- **No mobile apps in MVP.** Mobile-responsive web only; native apps are a later consideration.

## Success metrics (target / acceptable / minimum)

| Metric | Target | Acceptable | Minimum |
|---|---|---|---|
| Time to log a new project (lead intake) | <2 min | <5 min | <10 min |
| Time to generate invoice from project | <30 sec | <1 min | <3 min |
| Active projects supported per user/day | 50 | 20 | 10 |
| Page load (any view) | <500ms | <1.5s | <3s |
| BOQ upload to quote-ready | <30 sec for 100-line BOQ | <2 min | <5 min |
| Concurrent users (no degradation) | 50 | 20 | 10 |
| Test coverage | 85% | 75% | 65% |
| Uptime (after deploy) | 99.5% | 99% | 98% |

## Risks

| ID | Risk | Mitigation | Detection signal |
|---|---|---|---|
| R1 | Scope creep — feature requests from founders | SCOPE_GUARD.md as gatekeeper; every new feature needs an ADR | unplanned features in PRs |
| R2 | BOQ format variation across uploads | Validator + schema-first import; reject malformed with clear errors | upload failures > 5% |
| R3 | RBAC complexity | Start with 3 roles (admin, PM, viewer); grow only when needed | new permission checks scattered in code |
| R4 | DB schema churn | Alembic from day 1; never edit migrations after merge | accidental data loss in dev |
| R5 | Compliance tracking becomes unmaintainable | Versioned checklists (NBC 2016 vs 2024); checklists in DB not code | new code edit needed for every standards update |
| R6 | Document storage cost | Local fs in dev → **MinIO local in prod → S3 only when scale demands** (target plan — MinIO is NOT wired today; storage is local `uploads/`, see `docs/conventions.md`) | storage > 50GB in year 1 |
| R7 | Performance with many projects | Pagination + indexes from day 1; load test in wave-2 | slow list views |
| R8 | Vendor coordination email-vs-portal | Vendors get a lightweight portal in wave-5; email fallback always works | vendors asking for status manually |

## Constraints
- **Tech stack frozen:** Python 3.11 + FastAPI + Postgres + Celery + Redis + React + Vite + TS + Tailwind + shadcn/ui — Celery is a **chosen dependency, not yet implemented** (no worker exists; see `HIERARCHY.md`), and Redis is used only as a cache today
- **Self-hosted:** Single deployment for SWA; Docker Compose first, k8s later
- **Indian context:** INR primary currency, GST-aware invoicing, Gujarati/Hindi/English support in UI (English first)
- **GDPR-lite:** Personal data deletable on request; audit log for who accessed what

## Out for now (later waves)
- Client portal (read-only project access)
- Vendor portal (vendor self-service)
- Mobile apps
- Multi-tenancy
- AI assistant in-app (Project 1 result import is enough for now)
- Integration with Tally/Zoho Books
- WhatsApp notifications
