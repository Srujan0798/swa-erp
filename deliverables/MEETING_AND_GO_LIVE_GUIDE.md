# SWA ERP — Meeting and Go-Live Guide (FINAL)

**Use this file for the client meeting and screen share.** It merges the demo script,
trial script, Viraj/IT messages, and go-live checklist into one place, in simple words.

Canonical records (history, not meeting material):
`deliverables/SUBMISSION.md` · `deliverables/TECHNICAL_REPORT.md` ·
`deliverables/SEND_IT.md` · `deliverables/REPLY_VIRAJ.md` ·
`deliverables/handover/` · `resources/MEETINGS_MASTER.md`

---

## 1. One-line story (say first)

> "Today SWA runs work on about 20 Excel files. This system is the **same work flow** on a
> website — Inquiry, Client, Project, Agreement, Token, Document Number, Time, Invoice.
> Nothing new to learn, only faster and in one place."

## 2. Before the meeting (you, 15 minutes)

```bash
make dev                  # UI http://127.0.0.1:3100 · API http://127.0.0.1:8100
make swa-live-local       # real Excel data path (USE THIS for SWA)
```

- Login ready: `admin@swa.co.in` / `admin123!`
- Check: one Inquiry, one Client, one Agreement, one Token, one Document Reference visible.
- Fallback if UI is slow: `python3 scripts/smoke_chain.py` (prints live `SWA-…` IDs).
- Do NOT use `make seed-demo` for SWA — that is synthetic test data only.

## 3. Start-to-end process (show and say)

### Step 1 — Inquiry comes in
Open **Inquiries**. Show an ID like `SWA-2025-INQ-004`.
Say: "Every new work starts here, like the first row in your sheet."

### Step 2 — Client check (new vs existing)
Click **Convert**. Show both paths:
- Client exists (APEX / INNER are **client names**) → reuse it.
- Client is new → system creates `SWA-2025-CLT-…`.
Say: "The system checks the client list first, so no duplicate clients."

### Step 3 — Project + Service Agreement
Show the Project, then **Service Agreement** `SWA-2025-SA-…`.
Say: "Agreement is the yearly work promise with the client. Service name is
**INSUDESIGN** — that is the service, not a client."

### Step 4 — Token (unit of work)
Open **Tokens**, show `SWA-2025-TKN-…` under the agreement.
Say: "Each small work order under the agreement is one Token."

### Step 5 — Document Reference (drawing/document number)
Open **Document References**. Issue a DBR, then a KDR.
Say: "Drawings and documents get one shared number line —
`SWA-2025-DBR-001`, then `SWA-2025-DBR-002`. Same as your Excel numbering.
IDs restart every January: `…-2025-…-011` → `…-2026-…-001`."

### Step 6 — Time + Invoice + GST
Log billable time (15-minute style), open the invoice, point at GST fields.
Say: "Staff hours become the invoice. GST 18% is shown separately and added to the total."

### Step 7 — Compliance + dashboard
Open a project checklist: **NBC / ECBC / IGBC / IS**. Open the dashboard.
Say: "Safety and green checklists stay attached to the project. The dashboard shows
project and money summary."

## 4. Questions to ask them (write answers down)

**Data (most important):**
1. "Is this the same flow you do in Excel today? What is different?"
2. "Who will give the final frozen Excel files for upload?"
3. "Who will run the one-time Excel import — you, your person, or me on a call?"

**Server (only if Viraj/IT is present — do NOT re-ask answered items):**
4. Docker installed? WSL2 available? Which ports are free?
5. How do staff reach it — web address or IP? Who issues the HTTPS certificate?
6. Database inside Docker or Windows services? Existing backup process?
7. How do updates reach the server — remote access, commands, or your process?

**Already locked (do NOT reopen):** APEX/INNER = clients · INSUDESIGN = service name ·
yearly ID reset everywhere · no Leads module (Lead IDs removed).

## 5. Go-live checklist (in order)

1. [ ] Meeting confirms the flow matches Excel work.
2. [ ] Server facts answered → deploy per `docs/DEPLOYMENT_CHECKLIST.md`.
3. [ ] Viraj freezes Excel sheets → dry-run import (`make import-real`).
4. [ ] Review import report row by row → commit import (`make import-real-commit`).
5. [ ] Train staff with `deliverables/handover/USER_GUIDE.md` (user),
   `TRAINING_ONE_PAGER.md` (one page), `ADMIN_GUIDE.md` (admin).
6. [ ] Daily DB backup + file backup joined to existing server process.

## 6. Honest limits (say before they ask)

- Runs on my laptop today; **not yet on the company server** (needs server answers).
- Load test (10–150 users, no errors) was on a dev machine, not their server.
- Old Excel import is tested as a tool; the real one-time run waits on Viraj.
- Async export runs in the backend; no separate screen was requested.
- Client portal, vendor portal, mobile apps, Tally integration: **not built** (client excluded them).

## 7. Close (say last)

> "The system is ready. Two things remain on your side: server setup and the frozen
> Excel files. Give me those and we go live."
