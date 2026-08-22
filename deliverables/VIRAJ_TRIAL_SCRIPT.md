# SWA trial script (30–40 minutes) — real Excel path only

**Audience:** Viraj / SWA staff.  
**Goal:** Prove this is their sheet workflow on a website — not a student demo.

## Before the call (you)

```bash
make dev
make swa-live-local    # or: make bootstrap-real
```

Login ready: `admin@swa.co.in` / `admin123!`  
URL: http://127.0.0.1:3100

## Script

1. **Login** — open dashboard. Amber banner only if DB empty (should not be after `make swa-live-local`). Hint on login mentions that command.
2. **Inquiries (nav 1)** — open list. Point to a `SWA-2025-INQ-…` ID, Type, Technical lead columns from their extract. Convert path: check existing client → always land on a Project (Meeting 2).
3. **Clients (nav 2)** — Clients Sheet columns: Client ID, Name, Industry, Primary Contact, Email, Phone, Status, Date Onboarded. Real names from sheets (e.g. Shabnam / Halcyon — not `seed_demo`).
4. **Service Agreements (nav 3)** — show `INSUDESIGN` / SA IDs `SWA-2025-SA-…`, Client Name, End date, Notes.
5. **Tokens (nav 4)** — Tokens Sheet columns: Token ID, **Agreement ID** (`SWA-…-SA-…`), Type, SWA employee, Project owner, Client employee, Tokens Used.
6. **Document refs (nav 5)** — **Document Reference Sheet**. Show DRN/DBR/KDR/CON/GAD IDs, Author, Revision, Type, User, Project code. Point at the **DBR/KDR shared counter** banner (next preview). Create a row from this page (pick Associated Project) — same numbering as Excel. Say clearly: “Files / drawings” is uploads; this is numbering.
7. **Projects (nav 6)** — Project Tracking columns: Project ID, Client, Inquiry, Milestone, Team Leader, Project owner, Status. `swa-live-local` links converted inquiries → projects even when the Tracking sheet is empty; otherwise convert an inquiry live.
8. **Time logging (nav 7)** — Excel-parity fields (work type, activity, software, billable hours). Pick Project, then optionally pick Token/Doc Ref into Reference ID. Log a row if useful.
9. **Ask them:** “Is this the same flow you do in Excel today?” Capture gaps in writing.

## Do not

- Open Vendors / RFQs / Materials first (secondary).  
- Use `seed_demo` for this call.  
- Claim Windows Server is live — local trial only.

## After

Write notes → `work/reports/recovery/week-N-viraj-feedback.md`.
