# SWA ERP — Meeting and go-live (THE only meeting file)

Share the **app** (`http://127.0.0.1:3100`), not this markdown.  
Agent prompts live in `work/ASSIGN-TO-AGENTS.md` — not this file.

Jaydeep is not here to redesign. Viraj tagged him because there is **no IT department**. Win: **one server name + 1–2 hour slot + Excel freeze name**.

| | |
|---|---|
| URL | **http://127.0.0.1:3100** (not 3000) |
| Login | `admin@swa.co.in` / `admin123!` |
| Data | `make swa-live-local` — never `seed-demo` |
| Check | Dashboard **SWA operations**. `SWA-2025-INQ-001`. **`SWA-2025-SA-011` + INSUDESIGN** |

**Say first (45s):** Same ~20 Excel files, one website, same IDs. Locked: APEX/INNER = clients, INSUDESIGN = service, yearly reset, Lead ID gone. This is **my laptop**, not the office server. After a walkthrough I need: who has the server, a 1–2 hour slot, who freezes Excel.

**Show this order only** (do not open Files/drawings, Vendors, RFQs, Materials, Tasks):

1. Dashboard — strip 1–7  
2. Inquiries — `INQ-001` Converted, **`INQ-003` Level Infra = New** (convert live if they want)  
3. Clients — Shabnam / Halcyon (APEX/INNER are in **live** books, not this sample)  
4. Agreements — **SA-011 + INSUDESIGN** (ABCD/APPLE/GOOGLE here = clients). New Agreement is on this page  
5. Tokens — TKN-001… under SA-011. New Token is on this page  
6. Document refs — CON / DBR / CAS / GAD = **numbers**, not PDFs  
7. Projects — from converted inquiries  
8. Time → Invoices — 1h billable → New Invoice → ₹5,000 + 18% GST ₹900 = ₹5,900 → Mark sent/paid  

Ask: “Same as Excel today?”

**Ask (write names):** (1) Are you the Windows Server person? (2) 1–2 hours which day? (3) Free Docker Engine + WSL2 OK? (4) IP vs hostname week 1? (5) Gap list or nothing? (6) Who freezes OneDrive — one name? (7) Who runs import — one name? (8) First 3–5 users + roles?

**Do not say:** 100% complete, server live, 100+ users on their box. **Do not reopen:** APEX / INNER / Leads.

**Close:** Ready to install. Person + slot + freeze → go live.

If he has 5 minutes: Dashboard + SA-011/INSUDESIGN, then questions 1, 2, 6.

---

## Extra time — full click script

---

## 0. Status in 20 seconds (honest)

| Question | Answer you can say |
|---|---|
| Is the product built? | **Yes — the Excel chain.** Inquiry → Client → Project → SA → Token → Doc number → Time → Invoice+GST. Verified live on this laptop today. |
| Can we show it live today? | **Yes.** URL below. Data is **their sample Excel**, not `seed-demo`. |
| Is it on the company server? | **No.** No IT department. Need a person + the Windows Server. |
| Can staff stop using Excel today? | **Not until** install + freeze + import of the **live** OneDrive files. |
| Internship / submission? | Product v1.0.1 for the Excel MVP. Company go-live is still their step. Do not say 100% of every sidebar item. |

Do **not** say “100% complete” or “nothing left.” Say: **ready to walk through; ready to install when you give the machine and freeze the Excel files.**

---

## 1. Open this before they join (you)

App is the real-data path, not `seed-demo`.

| | |
|---|---|
| URL | **http://127.0.0.1:3100** (port **3100**, not 3000) |
| Login | `admin@swa.co.in` / `admin123!` |
| What is loaded | Their sample Excel extract (`resources/ERP Sheets`) |

**What you must see after login (if any of these is missing, stop and reload):**

- Dashboard titled **SWA operations** — not an empty amber “no data” banner
- Sidebar numbered **1. Inquiries … 7. Time logging**
- Inquiries: `SWA-2025-INQ-001` / `002` / `003`
- Service Agreements: `SWA-2025-SA-011` with service **INSUDESIGN**
- Tokens: `SWA-2025-TKN-001` … `004`
- Document refs: `SWA-2025-CON-001`, `DBR-002`, `CAS-003`, `GAD-004`

If the UI is down, in a terminal at the repo root:

```bash
# API must already answer: curl http://127.0.0.1:8100/healthz  → {"status":"ok"}
# UI:        cd src/frontend && npx vite --port 3100
# Real data: make swa-live-local
```

Fallback if the browser is slow: `python3 scripts/smoke_chain.py` prints live `SWA-…` IDs. Still narrate the same flow.

---

## 2. What this meeting is

**Audience:** Viraj and/or Jaydeep (tagged 17 Sep: “Yeah, I’ll see”).

**Win for today (leave with these, or the call failed):**

1. They **see** Inquiry → Client → Project → Agreement → Token → Doc number → Time → Invoice.
2. They say whether that matches Excel (gaps written down).
3. **One name** for the Windows Server.
4. **One name** for who freezes the live Excel files.
5. A **date** for a 1–2 hour install, or a clear “not this month.”

This is **not** a spec workshop. Do not ask them to design the product.

---

## 3. Say this first (~45 seconds)

> Today SWA runs work across about 20 Excel files on OneDrive. Everyone edits them live, so there is no single source of truth.
>
> This system is **that same work** on a website: Inquiry, Client, Project, Service Agreement, Token, Document number, Time, Invoice with GST. Same IDs you already use — `SWA-2025-INQ-001`, `SWA-2025-SA-011`.
>
> Three things you already confirmed are in the product: APEX and INNER are **client names**, INSUDESIGN is the **service**, IDs reset every year, and Lead ID is gone.
>
> I will share the screen and walk the flow. Then I need two things from you: who has the office server, and who freezes the live Excel for the one-time upload.

Then share **http://127.0.0.1:3100** (the app). Zoom in so IDs are readable.

---

## 4. Screen-share — start to end (click this order)

**Do not** open Vendors, RFQs, or Materials first. Those exist; they are not the Excel core.

Login is already filled with admin. Click **Sign in**.

---

### Beat 0 — Dashboard (1 min)

**Click:** Dashboard (top of sidebar).

**Show:** The seven-step strip: Inquiry → Client → Service Agreement → Token → Document Ref → Project → Time log.

**Say:** “This is the same chain as your sheets, in the same order as the left menu.”

If an amber empty-data banner appears, the real load did not run — do not continue with dummy data.

---

### Beat 1 — Inquiry comes in (3 min)

**Click:** **1. Inquiries**.

**Show and point:**

| ID | Client on the row | Status | Use it to say |
|---|---|---|---|
| `SWA-2025-INQ-001` | Shabham films | Converted | Already won → became a project |
| `SWA-2025-INQ-002` | PGPR Projects Limited | Converted | Same |
| `SWA-2025-INQ-003` | Level Infra & Consultants | **New** | Still open — we can convert this live |

**Say:** “Every new job starts here, like the first row on the Inquiries sheet. The ID is assigned by the system. You do not type it.”

**Click** `SWA-2025-INQ-003` (the New one).

**Show:** Client name, type (Design), technical lead, requirement summary — Excel columns, not invented CRM fields.

**Click:** **Convert to client** (Actions card).

**Show both paths in the dialog:**

- System looks up whether **Level Infra & Consultants** already exists.
- If yes → reuse that client.
- If no → create `SWA-YYYY-CLT-…`, then always create a **Project**.

**Say:** “Viraj’s words from meeting 2: first we inquire; if it converts we check the client list; if the client exists we add a project; if not we add the client then the project. That is this button.”

Complete convert if they want to see it. If time is tight, cancel and say INQ-001/002 already did this.

---

### Beat 2 — Clients (2 min)

**Click:** **2. Clients**.

**Show (from the Clients sheet extract):**

- `SWA-2025-CLT-001` **Shabnam** — HVAC, Dormant
- `SWA-2025-CLT-002` **Halcyon Technologies** — Pharmaceutical
- `SWA-2025-CLT-003` **Acme air curtains Xylopia labs**

**Say:** “These names and industries come from your Clients sheet, not fake seed data. In the live OneDrive file you also have names like APEX and INNER — those are **clients**, not agreement types. We already locked that.”

**Do not** hunt for a Lead ID column. It was removed on your instruction.

---

### Beat 3 — Service Agreement (2 min)

**Click:** **3. Service Agreements**. There is a **New Agreement** button (pick a client, service name defaults to INSUDESIGN). Use it if they ask to create; otherwise show the imported rows.

**Show the row that matches the WhatsApp example:**

| Agreement ID | Service name | Client | Dates |
|---|---|---|---|
| **`SWA-2025-SA-011`** | **INSUDESIGN** | ABCD | 2025-10-01 → 2026-03-31 |
| `SWA-2025-SA-012` | INSUDESIGN | APPLE | |
| `SWA-2025-SA-013` | INSUDESIGN | GOOGLE | |

**Say, slowly:**

> “INSUDESIGN is the **service product**. ABCD / APPLE / GOOGLE here are **clients**. That is why we asked about a fourth agreement type — there isn’t one. APEX and INNER are also client names in the live books.”

**Say:** “Next January this becomes `SWA-2026-SA-001`. Counter resets on every sheet. You confirmed that on 11 Aug.”

---

### Beat 4 — Token = one unit of work (2 min)

**Click:** **4. Tokens**. **New Token** is on this page (pick an agreement first). Show imported rows first.

**Show:** `SWA-2025-TKN-001` … `004`, type Query / Design, **Agreement ID** `SWA-2025-SA-011`.

**Say:** “A token is one work order under the yearly agreement — calculate, query, design. Same as the Tokens sheet. Not a login token.”

---

### Beat 5 — Document Reference = numbering (3 min)

**Click:** **5. Document refs**.

**Show:**

| ID | Document type |
|---|---|
| `SWA-2025-CON-001` | Concept Note |
| `SWA-2025-DBR-002` | Design Basis Report |
| `SWA-2025-CAS-003` | Calculation Sheet |
| `SWA-2025-GAD-004` | GA Drawing |

**Show:** the dashed **DBR / KDR shared counter** banner and the next-ID preview.

**Say:**

> “This page is the Document Reference sheet — the number. Sidebar **Files / drawings** is where PDFs are stored. Two different things, same as Excel vs a folder of drawings.”

If they want a live create: **New Document Reference** → pick an associated project → save → new `SWA-2025-…` ID appears.

---

### Beat 6 — Projects (1 min)

**Click:** **6. Projects**.

**Show:** rows linked from converted inquiries, e.g. Thermal Audit (`INQ-001`), Sound Masking (`INQ-002`), MEDIA ROOM (`INQ-003`).

**Say:** “Your Project Tracking sample file was headers only, so these projects were created from the inquiries — same rule as meeting 2. Live tracking sheet at go-live will import the real rows.”

---

### Beat 7 — Time + Invoice + GST (3 min)

**Click:** **7. Time logging**.

**Show:** pick a project, hours, **billable** flag, work type / activity / software (Excel time-sheet columns). 15-minute style.

Log one row if useful (e.g. 1.00 hour, billable).

**Click:** sidebar **Invoices** (under More — only after the core chain).

**Show:** select a project → **New Invoice** → one line (e.g. Design hours, qty 1, rate 5000) → GST **18%**. Live check today: subtotal ₹5,000 + GST ₹900 = **₹5,900**. Open the invoice → **Mark sent** / **Mark paid**.

**Say:** “Hours become the invoice. GST is a separate line, then added. Currency INR.”

---

### Beat 8 — Compliance + close the loop (1 min)

**Click:** **Compliance**.

**Show:** standards **NBC / ECBC / IGBC / IS** on a project.

**Say:** “Checklists stay on the project. Not a separate spreadsheet.”

Optional: **Sustainability** if they care about green / payback numbers.

Then back to **Dashboard**.

**Ask (write the answer):**

> “Is this the same flow you do in Excel today? What is different?”

---

## 5. Already locked — do not reopen

Viraj answered these. Treat them as closed unless **they** bring them up.

| Topic | Locked answer | In the product |
|---|---|---|
| APEX / INNER | **Client names** | Free-text client name |
| INSUDESIGN | **Service name**, not a 4th SA type | Free-text `service_name` on every SA in this extract |
| Yearly IDs | Reset every 1 Jan, **all sheets** | `SWA-2025-SA-011` → `SWA-2026-SA-001` |
| Leads / LDI | **No Leads module.** Remove Lead ID even historically | Column dropped. Excel “First Lead ID” ignored on import |

If they mention Vikrant / IT: “Understood — you said there is no IT department. That is why we need one person on the server, even if it is Jaydeep.”

---

## 6. Questions to ask (closed; write names/dates)

Ask after the walkthrough. One at a time. Do not paste the old 8-question wall.

### Must leave with (process)

| # | Ask exactly | Why |
|---|---|---|
| 1 | “Is this the same flow as Excel today? What should change before go-live — a list, or nothing?” | Product gaps. If they say nothing, install as-is. |
| 2 | “Who freezes the live OneDrive Excel on import day? **One name.**” | Everyone edits today; no freeze = dirty import. |
| 3 | “Who runs the one-time import — me on a call, Jaydeep, or a named admin?” | Tool is ready (`make import-real` dry-run, then commit). |
| 4 | “Who are the first 3–5 people to log in, and their role (admin / PM / designer / viewer)?” | You create accounts. |

### Must leave with (server) — Jaydeep if he is on the call

| # | Ask exactly | Default if they don’t know |
|---|---|---|
| 5 | “Are **you** the person for the Windows file-server (VPN, ~128 GB), or someone else?” | Need one name. |
| 6 | “Can we get **1–2 hours on that machine** this week or next? Which day?” | Install waits on this. |
| 7 | “Is Docker already there? If not, we install **free Docker Engine + WSL2** — OK?” | Free Engine. Not paid Desktop unless they already have it. |
| 8 | “What should staff type — **IP is fine for week 1**, or do you have a name like `erp.swa.local`?” | IP until they pick a name. |

### Only if there is time (do not lead with these)

Docker vs Desktop, free ports, HTTPS / internal cert vs self-signed, existing backup job, Postgres/Redis in Docker vs Windows services, how updates are copied. Full list lives in `SEND_IT.md` (already in the group). Missing answers delay **install**, not the demo.

---

## 7. Go-live after they say yes (order)

Do not skip. Do not invent hostname/ports.

1. They confirm the flow (or give a written gap list you can do in hours, not weeks).
2. Named person gives **1–2 hours** on the Windows Server.
3. You install with `docs/INSTALL_NO_IT.md` + `docs/DEPLOYMENT_CHECKLIST.md` (Docker Engine, compose, secrets, health check).
4. Viraj **freezes** Excel. You dry-run: `make import-real`. Review the row report together.
5. Commit import: `make import-real-commit` (or `scripts/import_excel.py … --commit` per sheet).
6. Create the 3–5 users. Hand `handover/TRAINING_ONE_PAGER.md` + `USER_GUIDE.md`.
7. Join daily DB backup + file backup to whatever they already use (`make backup-db` / `backup-files` until then).
8. Staff use the website over VPN. Excel becomes read-only archive.

---

## 8. Honest limits (say before they ask)

- **This screen is my laptop.** Not the office server.
- Load test (10–150 users, no errors) was on a **dev machine**. Their Windows Server has not been load-tested. Do not promise “100+ users” on their box.
- The extract on screen is the **sample** they gave (3 inquiries, 3 agreements, 4 tokens…). Live OneDrive is larger; same tool, frozen files. APEX/INNER are **not in this extract** — they are in the live books as client names.
- **Files / drawings** in the sidebar is file storage and is **not finished**. Document **numbers** are **5. Document refs**. Do not click Files first.
- Vendors / RFQs / Materials / Tasks exist as extra CRM; they are **not** the Excel MVP. Do not open them unless asked.
- Client portal, vendor portal, mobile apps, Tally, HR, complaints, marketing: **out of MVP** — Viraj dropped them in meeting 2.
- Redis is optional for this walkthrough. Login and the Excel chain work without it.

---

## 9. Close (say last)

> The system is ready. Two things remain on your side: a person and a slot on the office server, and a freeze of the live Excel files. Give me those and we go live. I can install in a short session and we import together so the data stays with SWA.

If they go quiet: “Jaydeep — are you the server person? If yes, send me a 1–2 hour slot. If not, tell me who is.”

---

## 10. Do not

- Do not open **Vendors / RFQs / Materials** first.
- Do not use `make seed-demo` / “Acme Demo” as the product.
- Do not re-send `SEND_IT.md` / `SEND_VIRAJ.md` as a wall of text.
- Do not reopen APEX / INNER / INSUDESIGN / yearly reset / Leads.
- Do not say the company server is live.
- Do not say “100% complete / zero risk.”
- Do not ask “what architecture should we use?”
- Do not click **Files / drawings** (that page is unfinished). Document numbering is **5. Document refs**.
- Do not convert a **Converted** inquiry — use `SWA-2025-INQ-003` (New) if you convert live.

---

## 11. If something breaks on the call

| Symptom | What to do |
|---|---|
| Login 500 / “column token_version” | DB drift — already patched on this machine (Alembic 0036). Restart API if needed. |
| Empty lists / amber banner | Re-run `make swa-live-local`. Do not show seed-demo. |
| Convert button missing | Inquiry already Converted, or your user is not PM/admin. Use INQ-003 or log in as admin. |
| UI not loading | Confirm you are on **:3100**. :3000 is a different app on this laptop. |
| They say “this is dummy” | Point at `SWA-2025-SA-011` + INSUDESIGN + Shabnam / Halcyon from **their** xlsx. Offer to import **their** live file next. |

---

## 12. Internship / submission (if they or college ask)

- Product **v1.0.1** — core Excel chain, GST invoices, RBAC, importer, Docker install path.
- Quality track (CI, tests, load on a **dev** machine) is documented in `SUBMISSION.md` / `README.md`.
- Not claimed: client-server load numbers; frontend function coverage is **below** the 60% threshold (state that if an evaluator asks).
- Remaining **client** work: server facts, Excel freeze + owner. Remaining **engineering** polish is not a meeting blocker.

---

## 13. WhatsApp if Jaydeep has no calendar slot

```
Jaydeep — thanks for jumping in.

I can walk the ERP live in 20 minutes (same Excel flow SWA uses today).
After that I only need:
1) who has the Windows Server
2) a 1–2 hour slot to install
3) who freezes the live Excel for the one-time import

Are you free today or tomorrow? I can share screen whenever you are.
```
