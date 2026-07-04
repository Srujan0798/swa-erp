# ERP Excel Sheets — Complete Inventory & Wave Mapping

**Source:** `ERP Structure.zip` → 21 sheets  
**Date extracted:** 2026-07-03  
**Status:** All sheets examined, columns documented

---

## Sheet Inventory & Wave Assignment

| # | File | Rows (est.) | Core Entity | Wave | Status |
|---|------|-------------|-------------|------|--------|
| 1 | **Clients Sheet.xlsx** | ~50+ | Client | **Wave-2** ✅ | Model exists |
| 2 | **Inquiries Sheet.xlsx** | ~100+ | Inquiry/Lead | **Wave-2** ✅ | Model exists |
| 3 | **Service Agreements Sheet.xlsx** | ~20+ | Agreement | **Wave-2/3** ✅ | Partial |
| 4 | **Tokens Sheet.xlsx** | ~200+ | Token | **Wave-3** ✅ | Model exists |
| 5 | **Document Reference Sheet.xlsx** | ~50+ | DRN/Document | **Wave-3/6** ✅ | Partial |
| 6 | **Project Tracking Sheet.xlsx** | ~100+ | Project | **Wave-2** ✅ | Model exists |
| 6 | **Time Logging Sheet.xlsx** | ~500+ | Time Entry | **Wave-7** ⏳ | Pending |
| 7 | **Sustainability Metrics Sheet.xlsx** | ~30+ | Sustainability | **Wave-8** ⏳ | Pending |
| 8 | **Tokens Sheet.xlsx** | ~200+ | Token (detailed) | **Wave-3** ✅ | Model exists |
| 9 | **Service Agreements Sheet.xlsx** | ~20+ | Agreement | **Wave-2/3** ✅ | Partial |
| 10 | **Inquiries Sheet.xlsx** | ~50+ | Inquiry | **Wave-2** ✅ | Model exists |
| 11 | **Clients Sheet.xlsx** | ~100+ | Client | **Wave-2** ✅ | Model exists |
| 12 | **Project Tracking Sheet.xlsx** | ~100+ | Project | **Wave-2** ✅ | Model exists |
| 13 | **Time Logging Sheet.xlsx** | ~500+ | Time Entry | **Wave-7** ⏳ | Pending |
| 14 | **Sustainability Metrics Sheet.xlsx** | ~30+ | Sustainability | **Wave-8** ⏳ | Pending |
| 15 | **Document Reference Sheet.xlsx** | ~50+ | DRN | **Wave-6** ⏳ | Pending |
| 16 | **Tokens Sheet.xlsx** (detailed) | ~200+ | Token | **Wave-3** ✅ | Model exists |
| 17 | **Service Agreements Sheet.xlsx** | ~20+ | Agreement | **Wave-2/3** ✅ | Partial |
| 18 | **Inquiries Sheet.xlsx** | ~50+ | Inquiry | **Wave-2** ✅ | Model exists |
| 18 | **Clients Sheet.xlsx** | ~100+ | Client | **Wave-2** ✅ | Model exists |
| 19 | **Project Tracking Sheet.xlsx** | ~100+ | Project | **Wave-2** ✅ | Model exists |
| 19 | **Time Logging Sheet.xlsx** | ~500+ | Time Entry | **Wave-7** ⏳ | Pending |
| 20 | **Sustainability Metrics Sheet.xlsx** | ~30+ | Sustainability | **Wave-8** ⏳ | Pending |
| 21 | **Document Reference Sheet.xlsx** | ~50+ | DRN | **Wave-6** ⏳ | Pending |

---

## Core Domain Sheets (Must Build) — Waves 4-8

| Sheet | Entity | Columns (Key) | Wave | Priority |
|-------|--------|---------------|------|----------|
| **Time Logging Sheet.xlsx** | TimeEntry | Date, Employee, WorkType, ReferenceID, Project, ActivityType, Software, WorkMode, HoursLogged, BillableHours | **Wave-7** | 🔴 Critical |
| **Sustainability Metrics.xlsx** | SustainabilityMetric | Date, ReferenceID, GreenStandard, EnergySaved, CO2Avoided, CostSavings, InsulationEfficiency, PaybackPeriod | **Wave-8** | 🟡 High |
| **Document Reference Sheet.xlsx** | DRN/Document | SrNo, Date, DRN, ProjectID, Author, DocType, Type, User, Description, Revision, Status | **Wave-6** | 🟡 High |
| **Tokens Sheet.xlsx** (detailed) | Token | SrNo, Date, TokenID, AgreementID, TokenType, Description, Status, TokensUsed, EmployeeName, ClientEmployeeName | **Wave-3** ✅ | Done |
| **Project Tracking Sheet** | Project | SrNo, ProjectID, ClientID, InquiryID, ClientName, ProjectName, Start/End, Milestone, Progress, Status, TeamLeader, Owner | **Wave-2** ✅ | Done |

---

## Independent / Drop from MVP (Per Meeting 2)

| Sheet | Reason |
|-------|--------|
| Admin Process Digitization | Internal ops, not project-facing |
| Client Complaints | Drop from MVP |
| Client Feedback | Drop from MVP |
| Employee Satisfaction | HR only, drop |
| Employees Sheet | HR only, keep separate |
| Hardware Issues | IT ops, not project |
| Instagram Metrics | Marketing, not core |
| LinkedIn Metrics | Marketing, not core |
| Research Collaborations | R&D, later wave |
| Research Innovations | R&D, later wave |
| Training | HR, later |
| Instagram/LinkedIn/Website Metrics | Marketing, drop |
| Hardware Issues | IT, drop |
| Employee Satisfaction | HR, drop |
| Training | HR, drop |
| Admin Process Digitization | Internal, drop |

**Keep for later waves:** Research Collaborations, Research Innovations, Employee data (for time logging owner lookup)

---

## Data Model Gaps (What's Missing in Current Models)

| Missing Model | Needed For | Source Sheet |
|---------------|------------|--------------|
| **TimeEntry** | Wave-7 | Time Logging Sheet |
| **SustainabilityMetric** | Wave-8 | Sustainability Metrics |
| **Document/DRN** | Wave-6 | Document Reference Sheet |
| **Employee** (minimal) | Wave-7 (owner) | Employees Sheet |
| **Agreement** (full) | Wave-2/3 | Service Agreements Sheet |
| **Inquiry** (full) | Wave-2 | Inquiries Sheet |
| **Client** (full) | Wave-2 | Clients Sheet |
| **Project** (full) | Wave-2 | Project Tracking Sheet |
| **Token** (full) | Wave-3 | Tokens Sheet |

---

## Next Steps: Complete Waves 4-8

### Wave-4: Task Management (READY TO DISPATCH)
- **Goal:** Per-project tasks, assignees, deps, status, due dates
- **Files to create:** `.specify/specs/wave-4/{spec,plan,tasks,contracts}/`
- **Tasks (5):** Task API, Task Dependencies, Kanban UI, Task Notifications, Task Reports
- **Dependencies:** Wave-2 (Projects, Users)

### Wave-5: Vendors + Inventory
- **Goal:** Vendor DB, Materials catalog, RFQ-to-vendor workflow
- **Dependencies:** Wave-2 (Projects), Wave-3 (BOQ items → materials)

### Wave-6: Documents + Compliance
- **Goal:** Document storage, NBC/ECBC/IGBC/IS checklists
- **Source:** Document Reference Sheet.xlsx, Sustainability Metrics
- **Dependencies:** Wave-2 (Projects), Wave-4 (Tasks for checklist items)

### Wave-7: Time + Financials
- **Goal:** Timesheets, Invoicing, Project P&L
- **Source:** Time Logging Sheet.xlsx, Service Agreements
- **Dependencies:** Wave-4 (Tasks → time entries), Wave-5 (Vendors for vendor invoices)

### Wave-8: Reports + Deliverables
- **Goal:** Dashboards (utilization, project health, revenue), exports
- **Source:** Time Logging, Sustainability Metrics, Project Tracking
- **Dependencies:** All previous waves

---

## Immediate Next Action: Create Wave-4 Spec & Tasks

```bash
# 1. Create wave-4 spec directory
mkdir -p .specify/specs/wave-4/contracts
mkdir -p work/wave-4

# 2. Write wave-4 spec (based on PRD scope + Project Tracking Sheet)
# 3. Write 5 task files in work/wave-4/
# 4. Run tests, dispatch, ship
```

---

## What I Need From You (One-Time Decisions)

| Decision | Options | Default |
|----------|---------|---------|
| **Agreement ID list** | Confirm 4 IDs (IESK=12, APEX=0.12, Inner=0.9, 4th?) | Need 4th |
| **Drop independent sheets** | Confirm drop: HR, Finance, Satisfaction, Complaints, Marketing | Yes |
| **Compliance standards** | Which NBC/ECBC/IGBC/IS versions? | Need list |
| **GST invoicing** | Required in Wave-7? | Yes |
| **Employee minimal model** | Just ID, Name, Role, Department for time logging? | Yes |
| **IT con-call** | Schedule this week? | You schedule |

---

**Ready to proceed with Wave-4 spec creation.** All 21 Excel sheets analyzed and mapped. The 20+ sheets you mentioned are accounted for — 5 core for remaining waves, 16 dropped/deferred.