# Scope Guard

What's IN scope vs OUT, written defensively to prevent scope creep.

## IN scope (MVP — waves 1–4)
- Auth + RBAC (5 roles: admin, pm, designer, auditor, viewer)
- Clients (CRM-lite)
- Projects (lifecycle: Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed)
- Quotation/BOQ workflow (upload BOQ JSON/Excel from any source; versions; approvals; send to client)
- Task management (per-project; assignees; dependencies; statuses)
- Audit log (every mutation)

## IN scope (Full — waves 5–8)
- Vendor management (vendor DB; RFQ-to-vendor; comparisons)
- Inventory (materials catalog; pricing)
- Documents (upload, version, link to project)
- Compliance tracking (NBC, ECBC, IGBC, IS fire code checklists per project)
- Time tracking (timesheets; billable/non-billable)
- Financials (invoicing with GST; payments; project P&L)
- Reports + dashboards (utilization, project health, revenue forecast)
- Deliverables (paper, patent, report, slides, demo)

## OUT of scope
- Multi-tenancy (single SWA install; productize later via separate ADR)
- Client portal (read-only client access — separate future wave)
- Vendor portal (vendor self-service — separate future wave)
- Mobile apps (responsive web only)
- AI features inside the ERP (Project 1 rfq2boq is upstream — ERP only consumes BOQ files)
- Drawing creation / CAD / BIM
- Replacement accounting (invoice + export only; not Tally/Zoho Books replacement)
- Real-time collaboration (WebSocket co-editing)
- WhatsApp/Slack/Telegram notifications (out of MVP)

## Out for now (maybe later — need ADR)
- Direct API integration with Tally / Zoho Books
- Multi-language UI (English first; Hindi/Gujarati later)
- Custom dashboards (fixed dashboards in MVP)
- Bulk operations on projects/clients
- Advanced search / full-text indexing (basic ILIKE in MVP)

## When in doubt
Ask the orchestrator's `interviewer` agent to interview you. If a feature isn't in this list, it doesn't get built without updating this file FIRST.
