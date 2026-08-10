# SWA Consultancy ERP — Progress Brief for Viraj

**From:** Srujan
**Date:** August 2026

---

## 1. Where the project stands

The ERP is **built, tested, and ready**. Everything you asked for is in:

- Clients, Inquiries, Service Agreements, Tokens, Projects, Document Referencing, Time Logging
- Quotations/BOQ, tasks, vendors & materials, documents, compliance tracking (NBC/ECBC/IGBC/IS), invoicing, dashboards
- The Excel → ERP import tool, ready to move the existing 20 sheets over as a one-time migration
- Full test suite passing (413 tests), packaged for release (v1.0.1)

The system replaces the Excel sheets with one source of truth, keeping the same business logic
staff already use — it is not adding new processes, it is digitizing the existing ones.

## 2. Three data questions (a sentence each is enough)

These are the only open items, and they are about your data — the system works either way,
but the right answers save a possible small fix after go-live:

1. **4th Service Agreement type** — the sample data contains a service name `INSUDESIGN`, but we
   only know of three verbally (IESK / APEX / Inner). Is INSUDESIGN a real fourth type, or was it
   a data-entry variant?
2. **Yearly ID numbers** — IDs look like `SWA-2025-SA-011`. Should the number restart at 001 on
   Jan 1 each year, or keep counting across years? (Either is a one-line setting.)
3. **`LDI-*` IDs** — is that the legacy form of an Inquiry ID, or something different? There is no
   "Leads Sheet" among the 21 source files, so the data alone doesn't answer it.

## 3. What happens next (the plan)

1. **IT call** — a separate brief with 8 questions is being sent to the IT team (Vikrant) about
   the server setup (Windows Server, 128 GB RAM, VPN). Once they answer, the system is deployed.
2. **Data migration** — after the system is on the server, the Excel data is imported as a
   one-time migration. You (or a person you nominate) runs it, so the real data is controlled
   by the company, not by the developer.
3. **Training** — staff guides (per-role walkthrough, one-page getting started, admin guide)
   are ready to hand over.

## 4. Nothing to worry about

- No external paid services, no internet exposure — it runs inside the company network over VPN,
  exactly like the current file server.
- If any of the three questions above go unanswered, nothing breaks — the system uses safe
  defaults, and any correction later is a one-line change.

Reply to this with answers to the three questions whenever convenient. The IT brief is going out
separately.
