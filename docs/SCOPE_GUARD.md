# Scope Guard — SWA ERP

> **Purpose**: Explicit IN / OUT / LATER declaration to prevent scope creep.
> Every PR, task, or wave must be traceable to an IN item. OUT items are explicitly rejected.
> LATER items are parked with a revisit trigger.

---

## IN — Currently in Scope (Active)

### Core Domains
- **Clients & Contacts** — CRUD, search, audit trail
- **Projects** — lifecycle: Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed
- **Quotations / BOQ** — ingestion (JSON/Excel), versioning, PDF export, approval workflow
- **Tasks** — Kanban board, assignments, dependencies, time tracking (15-min increments, billable flag)
- **Vendors** — registry, RFQ, comparison, PO generation
- **Inventory** — stock levels, reservations, consumption against BOQ
- **Documents** — upload, versioning, tagging, compliance linkage
- **Compliance Tracking** — NBC, ECBC, IGBC, IS fire codes (explicit references stored per project)
- **Time Tracking** — entries, approvals, utilization reports
- **Financials** — Decimal(18,2), INR default, multi-currency ready, invoicing, payments

### Technical Foundations
- **Auth** — JWT + RBAC. **Roles in production code** (`src/backend/core/roles.py`): `admin`, `pm`, `designer`, `auditor`, `viewer`.
  (Older SCOPE text listing `engineer`/`vendor` was stale — do not reintroduce without an ADR.)
  Hierarchy: admin ⊃ pm ⊃ {designer, auditor} ⊃ viewer.
- **API** — FastAPI, OpenAPI spec, Pydantic v2 schemas
- **Database** — PostgreSQL, SQLAlchemy 2, Alembic migrations
- **Frontend** — React 18, Vite, TypeScript strict, TailwindCSS, shadcn/ui, TanStack Query
- **Storage** — `StorageBackend` abstraction (local `uploads/`, opt-in MinIO via `STORAGE_BACKEND=minio`)
- **Async** — Celery + Redis (background export jobs)
- **Deploy** — Docker Compose (dev/prod), Makefile commands
- **Testing** — pytest (backend), Vitest + RTL (frontend), contracts as runnable tests
- **CI/CD** — GitHub Actions (lint, test, security), pre-commit hooks

### Governance & Process
- **Spec-driven** — `.specify/specs/wave-N/` contracts drive implementation
- **Wave pipeline** — `make dispatch wave=N` → `work/wave-N/` → `work/reports/wave-N/` → `make ship wave=N`
- **Orchestrator kernel** — `CLAUDE.md`/`KIMI.md`/`AGENTS.md`/`HIERARCHY.md`/`HANDOFF.md`/`HOW_TO_RUN.md`
- **Scope guard** — this file (PRs must reference IN item)
- **Archiving** — `attic/` for superseded work (never delete)

---

## OUT — Explicitly Out of Scope

| Item | Reason |
|---|---|
| **HR / Payroll** | Separate system; not consultancy ERP scope |
| **CRM / Lead Gen** | Leads enter at "Lead" stage; no marketing automation |
| **Full Accounting / GL** | Project financials only; no chart of accounts, tax filing |
| **Mobile App** | Responsive web only; no native iOS/Android |
| **Real-time Collaboration** | No concurrent editing, presence, comments v1 |
| **AI/ML Features** | No predictive scheduling, cost forecasting, auto-BOQ |
| **Multi-tenant SaaS** | Single-org internal tool; no tenant isolation |
| **Advanced BI / OLAP** | Operational reports only; no cube/warehouse |
| **Webhooks / Public API** | Internal API only; no external integrations v1 |
| **SSO / SAML / OIDC** | JWT local auth only; no enterprise identity federation |
| **Custom Workflow Engine** | Fixed project lifecycle; no user-defined states |
| **Document OCR / Parsing** | Manual upload only; no auto-extraction from PDFs |
| **Resource Scheduling / Gantt** | Task board only; no critical path, resource leveling |
| **Vendor Portal** | Vendors receive email/PO; no self-service portal |

---

## LATER — Parked for Future Waves

| Item | Trigger to Revisit |
|---|---|
| **Celery Background Workers** | When async export/import volume justifies it (currently sync OK) |
| **MinIO / S3 Storage** | When `uploads/` exceeds 50 GB or multi-host deploy needed |
| **Advanced Reporting / Dashboards** | When PMs request >5 custom reports/month |
| **Mobile PWA** | When >30% sessions are mobile |
| **Audit Log UI** | When compliance audit requires searchable trail |
| **BOQ Template Library** | When >10 repeated BOQ structures exist |
| **Vendor Performance Scorecards** | When vendor base >50 and rebid frequency >quarterly |
| **Integration: Accounting (Tally/Zoho)** | When finance team requests auto-sync |
| **Integration: Calendar (Google/Outlook)** | When task dates need calendar sync |
| **Notifications (Email/Slack/In-app)** | When stakeholders miss >2 task deadlines/month |
| **Custom Fields per Domain** | When >3 domains request non-standard attributes |
| **RBAC: Project-level Permissions** | When org grows >20 users with cross-project roles |
| **API Rate Limiting / Throttling** | When public API is IN scope |
| **Automated Backup/Restore Testing** | When RPO/RTO defined by leadership |

---

## Scope Change Protocol

1. **Propose** — Open issue/PR with `scope-change` label, cite IN/OUT/LATER table
2. **Review** — Orchestrator evaluates against project goal (internal ERP for SWA Consultancy)
3. **Decide** — Move to IN (with wave assignment), keep OUT, or promote from LATER
4. **Record** — Update this file; add entry to `CHANGELOG.md`
5. **Gate** — No code merges without scope guard approval

---

## Quick Reference for PR Authors

| Your Change Touches... | Required Scope Guard Check |
|---|---|
| New API endpoint | Is domain in IN? |
| New DB table/migration | Is domain in IN? |
| New UI page/component | Is domain in IN? |
| New dependency | Is it in tech stack (IN)? |
| Config change | Does it enable IN feature? |
| Test addition | Does it cover IN contract? |
| Refactor | No scope change (verify only) |

**If unsure → ask orchestrator before coding.**

---

*Last updated: 2026-09-20 | Next review: wave-1 completion*
