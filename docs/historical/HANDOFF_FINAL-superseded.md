# SWA ERP — FINAL HANDOFF DOCUMENT

**Project:** SWA ERP — Internal ERP for SWA Consultancy (insulation engineering)
**Date:** 2026-07-03
**Status:** Waves 1-3 SHIPPED | Wave-4 IN PROGRESS | Waves 5-8 QUEUED
**Total Tests:** 97/97 passing

---

## 📍 PROJECT STATUS SNAPSHOT

| Wave | Name | Status | Commit | Tests |
|------|------|--------|--------|-------|
| 1 | Foundation (Auth, RBAC, Users, Frontend) | ✅ SHIPPED | `df1b779` | 15/15 |
| 2 | Clients + Projects (CRM, Lifecycle) | ✅ SHIPPED | `d1e3017` | 52/52 |
| 3 | Quotation/BOQ (Upload, Versions, Quotes, PDF) | ✅ SHIPPED v0.2.0 | `f49eac1` | 97/97 |
| 4 | Task Management (Kanban, Deps, Comments) | 🚀 **IN PROGRESS** | — | — |
| 5 | Vendors + Inventory | ⏳ QUEUED | — | — |
| 6 | Documents + Compliance | ⏳ QUEUED | — | — |
| 7 | Time + Financials | ⏳ QUEUED | — | — |
| 8 | Reports + Deliverables | ⏳ QUEUED | — | — |

**Current Version:** `0.2.0` (pyproject.toml + package.json)
**Git Tags:** `wave-3-complete`

---

## 🏗️ ARCHITECTURE (FROZEN)

```
Browser (React 18, Vite, TS, Tailwind, shadcn/ui, TanStack Query)
           │ HTTPS + JSON + JWT
           ▼
┌──────────────────────────────────────────────────────────────┐
│ FastAPI (Python 3.11, uvicorn/gunicorn)                     │
│  ├── api/           routers per domain                       │
│  ├── services/      business logic                           │
│  ├── schemas/       Pydantic v2 models                       │
│  ├── models/        SQLAlchemy 2 ORM                         │
│  └── core/          config, security, deps                   │
└────┬──────────────┬──────────────┬───────────────────────────┘
     │              │              │
┌────▼────┐   ┌──────▼──────┐ ┌────▼────────────┐
│PostgreSQL│   │ Redis       │ │ Local FS / S3   │
│(primary) │   │ (Celery +   │ │ (uploads, docs, │
│          │   │  cache)     │ │  BOQs, export)  │
└─────────┘   └─────────────┘ └─────────────────┘
```

**Auth:** JWT (HS256 dev / RS256 prod) + RBAC (admin, PM, designer, auditor, viewer)
**Money:** `Decimal(18,2)`, INR default, GST-aware
**Files:** Local FS (dev) → MinIO (prod) → S3 ready
**Background:** Celery + Redis (email, PDF, reports)

---

## 📋 WHAT'S DONE (Waves 1-3)

### Wave 1 — Foundation ✅
- Auth (JWT + refresh), RBAC (5 roles), Users API
- Frontend shell (React + Vite + Tailwind + shadcn/ui)
- Docker Compose, CI, Alembic migrations

### Wave 2 — Clients + Projects ✅
- Client/Contact CRUD, search, pagination
- Project CRUD, lifecycle (Lead→Quote→Awarded→Design→Vendor→Execution→Validation→Closed)
- Dashboard with stats, project cards
- 52 tests passing

### Wave 3 — Quotation/BOQ ✅
- BOQ upload (JSON/Excel), parsing, validation
- BOQ versioning, approval workflow
- Quote generation, versioning, PDF export (WeasyPrint)
- Frontend BOQ/Quote UI
- 97/97 tests passing

---

## 🚀 CURRENT WORK: WAVE-4 (TASK MANAGEMENT)

**Spec created:** `.specify/specs/wave-4/spec.md`
**Plan created:** `.specify/specs/wave-4/plan.md`
**Tasks defined:** `.specify/specs/wave-4/tasks.md`
**Contracts:** `.specify/specs/wave-4/contracts/test_wave4_contracts.py` (all 5 test classes)

**5 Tasks to Implement:**
1. `work/wave-4/01-task-models-api.md` — Models, repos, CRUD API, RBAC
2. `work/wave-4/02-task-dependencies-api.md` — DAG, cycle detection, blocked status
3. `work/wave-4/03-task-comments-notifications.md` — Comments, Celery email, in-app notifications
4. `work/wave-4/04-frontend-kanban-board.md` — Drag-drop Kanban (dnd-kit)
4. `work/wave-4/05-frontend-task-detail.md` — Task modal, comments, deps, time-log link

**Next:** Run contract tests → implement → lint → test → ship → tag `wave-4-complete` → v0.3.0

---

## 📦 WHAT'S NEEDED FROM STAKEHOLDERS (5 DECISIONS)

| Decision | Options | Impact |
|----------|---------|--------|
| **4th Agreement ID** | Have 3 (IESK=12, APEX=0.12, Inner=0.9) | Data model |
| **Drop independent sheets** | HR, Finance, Satisfaction, Complaints, Marketing | Scope reduction |
| **Compliance versions** | NBC 2016/2024, ECBC 2017, IGBC, IS fire codes | Wave-6 schema |
| **GST invoicing** | Required in Wave-7? | Invoice schema + PDF |
| **Migration owner** | Dev team vs internal admin | Timeline |

**Infrastructure (from Meeting 2):**
- Windows Server (128GB RAM) + Docker Desktop + MinIO + PostgreSQL + Redis
- IT con-call needed this week

---

## 🗂️ DATA SOURCE: 21 EXCEL SHEETS (MAPPED)

**Core (Waves 4-8):**
| Sheet | Entity | Wave |
|-------|--------|------|
| Time Logging Sheet.xlsx | TimeEntry | 7 |
| Sustainability Metrics.xlsx | SustainabilityMetric | 8 |
| Document Reference Sheet.xlsx | DRN/Document | 6 |
| Tokens Sheet.xlsx | Token (detailed) | 3 ✅ |
| Project Tracking Sheet | Project | 2 ✅ |

**Drop from MVP (per Meeting 2):**
Admin Process, Client Complaints, Client Feedback, Employee Satisfaction, Employees, Hardware Issues, Instagram/LinkedIn/Website Metrics, Research Collaborations, Research Innovations, Training, Hardware Issues

---

## 🛠️ TECH DEBT / FIXES NEEDED

| Area | Issue | Priority |
|------|-------|----------|
| Frontend TS | 15+ errors (Badge import, unused vars, type mismatches) | High |
| Backend lint | 94 ruff errors (56 unfixed) | Medium |
| Datetime UTC | `datetime.utcnow()` deprecation warnings | Low |
| E2E tests | Playwright needs vitest dependency | Medium |

---

## 📁 KEY FILES & LOCATIONS

| File | Purpose |
|------|---------|
| `plan/ARCHITECTURE.md` | Full architecture (159 lines) |
| `plan/PRD.md` | Requirements (73 lines) |
| `plan/EXECUTION.md` | Wave status & dependency graph |
| `HANDOFF.md` | Current state + next actions |
| `resources/MEETING_1_CLEAN.md` | Client flow, tokens, access matrix |
| `resources/MEETING_2_CLEAN.md` | Infra, modules, migration, scope |
| `resources/EXCEL_SHEETS_INVENTORY.md` | 21 sheets → wave mapping |
| `resources/ERP Structure.zip` | 21 source Excel sheets |
| `.specify/specs/wave-4/` | Wave-4 spec, plan, tasks, contracts |
| `work/wave-4/` | 5 task implementation guides |

---

## 🎯 IMMEDIATE NEXT ACTIONS

### 1. Stakeholder Meeting (This Week)
- [ ] Show architecture (1 page)
- [ ] Ask 4 question groups (Infra, Migration, Scope, Architecture)
- [ ] Get 5 decisions above

### 2. Complete Wave-4 (Me, Now)
```bash
# 1. Run contract tests (will fail - no impl yet)
pytest .specify/specs/wave-4/contracts/ -v

# 2. Implement 5 tasks in work/wave-4/
# 3. Run tests → lint → format
# 3. Ship: version bump → changelog → tag → commit
```

### 3. Waves 5-8 (Sequential)
| Wave | Source Data | Est. |
|------|-------------|------|
| 5 Vendors + Inventory | Service Agreements, Tokens | 45 min |
| 6 Documents + Compliance | Document Reference, Sustainability | 45 min |
| 7 Time + Financials | Time Logging, Service Agreements | 45 min |
| 8 Reports + Deliverables | Time Logging, Sustainability, Project Tracking | 45 min |

**Total remaining: ~3.5 hours**

---

## 🔐 SESSION PROTECTION (CRITICAL)

**Current OpenCode Session:** `ses_0e1a36183ffeZNFUcDhYS5htHg`
**Protected in:** `/Users/srujansai/Desktop/kleenhand.md` (CRITICAL RULE)
- Never auto-delete current session
- Exclude from ALL deletion queries: `AND id != '$CURRENT_SESSION'`
- Export before any deletion consideration: `opencode export <SESSION_ID>`

---

## 📝 CHANGELOG (v0.2.0)

```
## [0.2.0] — 2026-07-03
### Added
- Wave-3: Quotation / BOQ Workflow — BOQ upload (JSON/Excel), versioning, quote generation, PDF export, frontend UI
- Wave-3 acceptance tests: 5/5 passing
```

---

## 🏁 COMPLETION CRITERIA (PROJECT DONE)

- [ ] Waves 4-8 shipped (tags `wave-4-complete` ... `wave-8-complete`)
- [ ] All 97+ tests passing per wave
- [ ] Frontend TS clean (0 errors)
- [ ] Backend lint clean (ruff + black)
- [ ] E2E tests passing (Playwright)
- [ ] Version `0.7.0` tagged
- [ ] `CHANGELOG.md` complete
- [ ] `HANDOFF.md` updated to "PROJECT COMPLETE"
- [ ] Deploy guide for Windows Server + Docker + MinIO

---

**Handoff prepared by:** AI Orchestrator
**For:** Stakeholder review + continued implementation
**Next update:** After Wave-4 ship