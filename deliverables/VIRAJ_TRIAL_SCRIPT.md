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

1. **Login** — open dashboard. Point at the amber banner if empty (should not be empty after bootstrap).
2. **Inquiries (nav 1)** — open list. Point to a `SWA-2025-INQ-…` ID from their extract.
3. **Clients (nav 2)** — show real client names from sheets (not “Acme demo”).
4. **Service Agreements (nav 3)** — show `INSUDESIGN` / SA IDs `SWA-2025-SA-…`.
5. **Tokens (nav 4)** — units of work under SA.
6. **Document refs (nav 5)** — **this is the Document Reference Sheet**. Show DRN/DBR/KDR-style IDs. Say clearly: “Files / drawings” is uploads; this is numbering.
7. **Projects (nav 6)** — if sample Project Tracking sheet was empty, convert an inquiry → project live (Meeting 2 rule: check client exists → always land on project).
8. **Time logging (nav 7)** — log hours against a project/token if data allows.
9. **Ask them:** “Is this the same flow you do in Excel today?” Capture gaps in writing.

## Do not

- Open Vendors / RFQs / Materials first (secondary).  
- Use `seed_demo` for this call.  
- Claim Windows Server is live — local trial only.

## After

Write notes → `work/reports/recovery/week-N-viraj-feedback.md`.
