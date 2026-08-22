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
2. **Inquiries (nav 1)** — open list. Point to a `SWA-2025-INQ-…` ID, Type, Technical lead columns from their extract.
3. **Clients (nav 2)** — show real client names from sheets (e.g. Shabnam / Halcyon — not synthetic `seed_demo` names).
4. **Service Agreements (nav 3)** — show `INSUDESIGN` / SA IDs `SWA-2025-SA-…`, Client Name, End date, Notes.
5. **Tokens (nav 4)** — Tokens Sheet columns: Token ID, Type, SWA employee (e.g. Mihir), Client employee, Tokens Used.
6. **Document refs (nav 5)** — **this is the Document Reference Sheet**. Show DRN/DBR/KDR/CON/GAD IDs, Author, Revision, Type, User. Say clearly: “Files / drawings” is uploads; this is numbering.
7. **Projects (nav 6)** — `swa-live-local` links converted inquiries → projects even when Project Tracking sheet is empty. Otherwise convert an inquiry live (Meeting 2: check client → always land on project).
8. **Time logging (nav 7)** — show Excel-parity fields (work type, activity, software, billable hours). Log a row if useful.
9. **Ask them:** “Is this the same flow you do in Excel today?” Capture gaps in writing.

## Do not

- Open Vendors / RFQs / Materials first (secondary).  
- Use `seed_demo` for this call.  
- Claim Windows Server is live — local trial only.

## After

Write notes → `work/reports/recovery/week-N-viraj-feedback.md`.
