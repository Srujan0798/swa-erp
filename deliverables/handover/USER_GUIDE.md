# SWA ERP — User Guide

How the system is used day to day, by role. Everything below is built and works
end to end (verified in wave-12's live API smoke test). It replaces the old
Excel sheets with the same business flow you already use — Inquiry → Client →
Project → Agreement → Token → Document → Time → Sustainability.

---

## The chain, in one picture

```
Inquiry (lead) → Client + Project → Service Agreement (retainer) →
Token (unit of work) → Document Reference (each report/drawing) →
Time logged → Sustainability metrics (if client shares them)
```

Every record gets a unique ID in the company format: `SWA-YYYY-XXX-001`
(e.g. `SWA-2026-INQ-001`, `SWA-2026-SA-001`, `SWA-2026-TKN-001`).

---

## PM (Project Manager)

1. **New lead?** Create an **Inquiry** (`SWA-…-INQ-…`).
2. **Got the client?** Use *Convert* on the inquiry — this creates the **Client**
   and a **Project** in one step.
3. **Recurring client?** Create a **Service Agreement** (`SWA-…-SA-…`) — an
   annual contract/retainer.
4. **Work to request?** Issue **Tokens** (`SWA-…-TKN-…`) — each is one unit of
   work (e.g. "calculate R-value").
5. **Track status** of the project as it moves through its lifecycle, and assign
   the team.
6. Log your own **time** against the project/token.

## Designer

1. Open the **Project** you're working in.
2. Produce documents → create a **Document Reference** for each report/drawing
   (`SWA-…-DRAWING-…` etc.). Its primary link is the **Project** (optionally a
   Token).
3. Log your **time** on the work you did.
4. For certification work (Reforge/DPR), create those document references — the
   **Auditor** reviews them.

## Auditor

1. Review **compliance checklists** (building-code standards: NBC / ECBC / IGBC /
   IS) attached to projects.
2. Handle **Reforge / DPR / certification** document references — review and
   certify them.
3. Read-only on most other data; your job is sign-off, not data entry.

## Admin

You can do **everything above**, plus:
- **User management** — create accounts and assign the 5 roles. See the
  *Administrator Guide* (`deliverables/handover/ADMIN_GUIDE.md`) for the exact
  procedure; don't duplicate it here.
- Finance / HR data is admin-only (and largely out of MVP scope).

## Viewer

Read-only. Navigate clients, projects, documents, dashboards. You cannot create
or edit anything — the system enforces this.

---

## A few plain-language notes

- **IDs are generated for you** — you don't type `SWA-2026-INQ-001`; the system
  assigns it when you save.
- **Documents** (PDFs, drawings, Word files) are uploaded and stored separately
  from the database, so the system stays fast.
- **Time logging** is per project/token — just enter the hours you worked.
- **Sustainability metrics** are optional and only filled in when a client shares
  energy/carbon savings data.

## If something looks wrong

Tell your **Admin** (or the person who runs the system). Common fixes are in the
Administrator Guide's troubleshooting section. Don't edit the database directly.
