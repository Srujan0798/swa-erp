# Meeting 2 — Infrastructure, Architecture & Module Scope (Clean Transcript)

**Date:** [Insert Date]
**Participants:** Viraj (Founder), Balram (Team), IT Person (pending), [Your Name]
**Purpose:** Finalize infrastructure, confirm module scope, align on data migration.

---

## 1. Production Infrastructure (Confirmed)

| Item | Decision |
|------|----------|
| **OS** | Windows Server (on-prem) — 99% confirmed |
| **RAM** | 128 GB (extendable) |
| **Capacity** | 100+ concurrent users via VPN/RDP — *wave-35 note: IT's claim about the server; our load tests verified 10/50/100/150 users on a dev machine, no server errors — `docs/PERFORMANCE.md`* |
| **Current load** | File storage only; some RDP sessions |
| **Network** | VPN access; shortcut in user folders |
| **Database** | PostgreSQL (user OK with SQL) |
| **File storage** | MinIO (S3-compatible) on same server |
| **Containerization** | Docker Desktop on Windows Server |
| **IT Contact** | Viraj to introduce server admin for con-call |

**Action:** Schedule con-call with IT person this week to finalize:
- PostgreSQL + Redis on Windows (Docker)
- MinIO setup
- Celery worker as Windows service
- Backup strategy (daily DB dump, weekly file backup)

---

## 2. Application Architecture (Current)

```
Browser (React) → FastAPI (Python 3.11) → PostgreSQL
                                    ↘ Redis (Celery broker)
                                    ↘ MinIO / Local FS (uploads)
```

- **APIs:** Internal REST (FastAPI) — no paid external APIs
- **Auth:** JWT (HS256 dev, RS256 prod) + RBAC
- **Background jobs:** Celery + Redis (email, PDF, reports)
- **PDF:** WeasyPrint (HTML→PDF)
- **Excel:** openpyxl import/export

---

## 3. Module Scope — 5 Modules for MVP (Waves 1-4)

| Module | Status | Notes |
|--------|--------|-------|
| **Inquiries** | Wave-2 (done) | ML → Client conversion |
| **Service Agreements** | Wave-2 (done) | Annual contracts per client |
| **Tokens** | Wave-3 (done) | Continuous numbering, Agreement ID link |
| **Projects** | Wave-2 (done) | Lifecycle: Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed |
| **Document Referencing + Time Logging** | Wave-4 (next) | Per-project + non-project (R&D, Marketing) |

**Agreed:**
- ✅ 5 modules for MVP
- ❌ Client Complaints & Satisfaction → **drop from MVP**
- ❌ Independent sheets (HR, Finance, Marketing, R&D) → **drop from MVP** or separate app
- ✅ Focus only on **interconnected chains** (Inquiry → Client → Agreement → Token → Project → Doc Ref → Time Log)

---

## 3. Data Migration (Critical)

| Source | Status | Owner |
|--------|--------|-------|
| **20 Excel files** | On OneDrive | Balram/Team |
| **Current access** | Read-only not possible (live editing) | — |
| **Migration owner** | **UNRESOLVED** — need decision | ? |
| **Approach** | One-time import → ERP becomes source of truth | Dev team? |

**Decision needed:** Who builds/runs the migration scripts? (Dev team vs. internal admin)

---

## 4. Wave Progress (Demoed)

| Wave | Scope | Status |
|------|-------|--------|
| 1 | Foundation (Auth, RBAC, Users, Frontend) | ✅ |
| 2 | Clients + Projects (CRUD, Lifecycle, Dashboard) | ✅ |
| 3 | BOQ/Quotation (Upload JSON/Excel, Version, Quote, PDF) | ✅ |
| 4 | Task Management (Kanban, Deps, Assignees) | ✅ (demoed) |
| 5 | Vendors + Inventory | ⏳ |
| 6 | Documents + Compliance | ⏳ |
| 7 | Time + Financials | ⏳ |
| 8 | Reports + Dashboards | ⏳ |

**Backend tests:** 97/97 passing
**Frontend:** TypeScript errors to fix (Badge import, unused vars, type mismatches)

---

## 5. Open Questions for Stakeholders

| Question | Decision Needed From |
|----------|----------------------|
| **Production OS** | Windows Server + Docker confirmed? | Viraj + IT |
| **Migration owner** | Who builds Excel→ERP import? | Viraj |
| **Independent sheets** | Drop HR/Finance/Complaints from MVP? | Viraj |
| **Client portal** | Wave-8 or later? | Viraj |
| **GST invoicing** | Required in Wave-7? | Viraj + Finance |
| **Compliance versions** | Which NBC/ECBC/IGBC/IS years? | Viraj + Auditor |
| **IT con-call** | Schedule this week? | Viraj → IT person |

---

## 6. Immediate Action Items

| Item | Owner | Deadline |
|------|-------|----------|
| Schedule IT con-call | Viraj | **This week** |
| Share 20 Excel files | Balram | **ASAP** |
| Confirm migration owner | Viraj | **Before Wave-4** |
| Confirm drop list (independent sheets) | Viraj | **Before Wave-4** |
| Provide Agreement ID list | Viraj | **Before Wave-4** |
| Share compliance standard versions | Viraj | **Before Wave-6** |
| GST invoice requirement | Viraj/Finance | **Before Wave-7** |