# Scope Guard

What's IN scope vs OUT, written defensively to prevent scope creep.

**Updated 2026-07-20** — the original version of this file defined MVP as "waves 1-4" (a generic
Client/Project/BOQ/Task CRM). That framing is now known to be wrong: waves 1-8 all shipped, but
they built a generic CRM, not the specific Inquiry→Client→Service Agreement→Token→Document
Reference chain the client actually asked for in Meeting 1/2 (see
`docs/decisions/0002-core-id-chain-gap.md`). Wave-9 closed that gap. **The real MVP boundary is
now waves 1-13, not waves 1-4** — see below.

## SHIPPED — generic CRM (waves 1-8)
- Auth + RBAC (5 roles: admin, pm, designer, auditor, viewer)
- Clients (CRM-lite) + Projects (lifecycle: Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed)
- Quotation/BOQ workflow (upload BOQ JSON/Excel; versions; approvals; send to client)
- Task management (per-project; assignees; dependencies; statuses)
- Vendor management, materials/inventory, RFQ-to-vendor
- Documents (generic file upload/version) + compliance tracking (NBC/ECBC/IGBC/IS checklists)
- Time tracking, invoicing (GST), project P&L
- Reports + dashboards, exports
- Audit log (every mutation)

## SHIPPED — the actual client-requested core chain (waves 9-13)
This is the part that matters most — it's what Meeting 1/2 actually asked for, distinct from the
generic CRM above:
- Inquiry (lead capture, `SWA-{year}-INQ-{seq}`) → conversion flow that checks for an existing
  Client by name before creating a new one, always lands on a Project (see ADR-0002 §3)
- Service Agreement (`SWA-{year}-SA-{seq}`, annual per-client retainer, `service_name` free text)
- Token (`SWA-{year}-TKN-{seq}`, unit of work under an Agreement)
- Document Reference / DRN (`SWA-{year}-{TYPE}-{seq}`, tied to Project required + Token optional;
  DBR/KDR share one counter, other doc types free-text)
- Sustainability metrics (post-project, Yes/No green-standard compliance + energy/CO2/payback data)
- Excel → ERP one-time import tooling (dry-run by default, idempotent, wave-13)
- Independent verification of the whole stack (real Docker boot, E2E, migration-chain integrity — wave-12)

## IN scope — infra/quality hardening (waves 14-16 — SHIPPED, corrected 2026-07-21)
- Docker Compose auto-migration on boot + fixing the dual-Postgres seed-script bug (wave-14)
- Fixing the 2 failing Playwright E2E selectors (wave-15)
- Sweeping remaining models (Material, Contact, ComplianceItem, etc.) for the same
  model/migration drift pattern found in Task and Document during wave-12 (wave-16)

## OUT of scope (unchanged, still confirmed by the client — Meeting 1 §3/§7, Meeting 2 §3)
- HR, Finance (beyond invoicing/P&L already built), Employee Satisfaction, Client Complaints/
  Satisfaction, Marketing metrics (Instagram/LinkedIn/website), Research Collaborations/
  Innovations — explicitly dropped from MVP by Viraj, "independent chains" per Meeting 2
- Multi-tenancy (single SWA install; productize later via separate ADR)
- Client portal (deferred — Meeting 2 explicitly left this as "wave-8 or later," still not started)
- Vendor portal (vendor self-service — separate future wave)
- Mobile apps (responsive web only)
- AI features inside the ERP (Project 1 rfq2boq is upstream and a genuinely separate product —
  never call it directly; this rule exists because of a real mix-up caught in Meeting 2, see
  `resources/MEETINGS_MASTER.md` §Meeting 2 point 9)
- Drawing creation / CAD / BIM
- Replacement accounting (invoice + export only; not Tally/Zoho Books replacement)
- Real-time collaboration (WebSocket co-editing)
- WhatsApp/Slack/Telegram notifications

## Out for now (maybe later — need ADR)
- Direct API integration with Tally / Zoho Books
- Multi-language UI (English first; Hindi/Gujarati later)
- Custom dashboards (fixed dashboards for now)
- Bulk operations on projects/clients
- Advanced search / full-text indexing (basic ILIKE for now)

## Pending go-live (not new features — do not expand MVP)

- **Data Qs from Viraj (2026-08): closed** — APEX/INNER = clients, INSUDESIGN = service name,
  yearly ID reset, no Leads sheet. See ADR-0002. No code change.
- **Migration owner** — still Viraj's call at go-live (who runs Excel import).
- **Server install facts** — no IT department; Viraj gets answers when free. Blocks company
  deploy config only. Do **not** invent hostname/ports or build alternate products while waiting.
  When ready: `docs/INSTALL_NO_IT.md` + `docs/DEPLOYMENT_CHECKLIST.md`.

## When in doubt
Ask the orchestrator's `interviewer` agent to interview you. If a feature isn't in this list, it
doesn't get built without updating this file FIRST.
