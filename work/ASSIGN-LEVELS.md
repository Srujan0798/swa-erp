# 10-level agent ladder (THE dispatch pack)

Grok does **not** run these. You paste. After a level’s reports exist, paste the **next** level. Stop at 10.

**Only two live files for humans:**
- This file → agents
- `deliverables/MEETING_AND_GO_LIVE_GUIDE.md` → Jaydeep tomorrow

Do **not** create `ASSIGN-v2` or extra meeting guides. `ASSIGN-TO-AGENTS.md` / `ASSIGN-PHASE-2.md` are pointers here.

**Loop:** Level N done ⇒ start N+1. Missed work is what the next level exists for.  
**Out of all 10 levels:** client portal, vendor portal, HR, complaints, marketing, Tally, AI, CAD/Word, WhatsApp. Viraj dropped them.

---

## SHARED (paste on every agent, every level)

```
You work in /Users/srujansai/Desktop/swa-erp. Read work/ASSIGN-LEVELS.md.
Do ONLY the AGENT id you were given (e.g. L3-A).

NOT A DEMO. Daily ERP for SWA Consultancy (Viraj Shah; Jaydeep Varu).
₹50K only if it really works. Meeting TOMORROW. CEO/CFO/technical may sit in.

No fake data, dead buttons, "coming soon", new frameworks, new UI kits, *_v2.md.
Edit existing files. git mv → docs/historical/ or attic/. NEVER delete.
Do NOT commit unless the user says YOUR files. Do NOT push. Do NOT git add -A.
Do NOT blindly revert. First: git status -sb ; git log --oneline -10 ; git diff --stat

LOCKED:
1. APEX/INNER = clients. INSUDESIGN = service. Not a 4th SA type.
2. Yearly IDs everywhere: SWA-2025-SA-011 → SWA-2026-SA-001. Don't change policy.
3. Lead ID/LDI gone even historically. First Lead ID ignored. No Leads module.
4. Flow: Inquiry → Client → Project → SA → Token → Doc Ref → Time → Invoice/GST
   → Compliance + Dashboard.
5. Docker/WSL2/ports = ask Jaydeep. Don't block.

NEVER claim 100% complete, server live, 100+ users on THEIR box, "thresholds met"
without a FRESH Python 3.11 paste. Frontend funcs were 58.45% < 60%.
NEVER fabricate. Else NOT MEASURED.

make swa-live-local (NEVER seed-demo)
http://127.0.0.1:3100  admin@swa.co.in / admin123!
Python 3.11. Docker DEAD. One pytest at a time.

Meeting file: deliverables/MEETING_AND_GO_LIVE_GUIDE.md (refine, never fork)
Report ONLY: work/reports/dispatch-24h/<AGENT-ID>.md
```

**How you assign a level:** SHARED + each agent block. Wait for reports before the next level.

---

# LEVEL 1 — freeze + Excel chain + meeting (start now)

**Gate:** none. **Done when:** `work/reports/dispatch-24h/AGENT-1.md` … `AGENT-6.md` (or `L1-*.md`) exist.

### L1-1

```
AGENT L1-1 only. You block L1-2..6 until done.
1. Split dirty files: meeting-critical vs other-worker. ASK user before commit.
   KEEP if present: AgreementsPage, TokensPage, InvoicesPage, DashboardPage,
   lib/api.ts, invoice_repo.py, inquiry_service.py, auth_service.py,
   alembic 0036, MEETING_AND_GO_LIVE_GUIDE.md, ASSIGN-LEVELS.md
2. Python 3.11: pytest+cov; cd src/frontend && npx vitest run --coverage;
   ruff, black --check, mypy; tsc, eslint, vite build; alembic heads (one).
3. Paste numbers. If frontend funcs < 60%: BELOW THRESHOLD.
4. Wave 49/50/51: this paste or NOT MEASURED. Fix ACTIVE.md.
   git log -S fresh_session_factory — landed or NOT FOUND.
Report: work/reports/dispatch-24h/AGENT-1.md
```

### L1-2

```
AGENT L1-2 only. Backend Excel chain. No new modules.
Convert: New+Contacted; reuse or create client; always Project; yearly CLT/PRJ IDs.
SA: free-text INSUDESIGN. Token under agreement.
Doc ref: project+doc_date; DBR/KDR share counter.
Time: 15-min, billable. Invoice: Decimal 18,2 INR; GST 18%; draft→sent→paid; seq IF NOT EXISTS.
Import ignores First Lead ID / LDI.
Acceptance: python3 scripts/smoke_chain.py prints SWA- IDs, then make swa-live-local (smoke pollutes).
Report: work/reports/dispatch-24h/AGENT-2.md
```

### L1-3

```
AGENT L1-3 only. Wire or remove dead buttons. No new pages. Files/drawings stays stub.
:3100 after swa-live-local, admin: New Inquiry; Convert INQ-003; Convert 300 uses detail.candidates;
New Agreement on Agreements list; New Token on Tokens list; New DBR; time 1.00h;
invoice GST 18% not 1800%; Mark sent/paid; delete 204 no JSON toast; no Smoke/Acme/lorem.
Click INQ-001/003, SA-011+INSUDESIGN, TKN-001..004, CON/DBR/CAS/GAD.
Report: work/reports/dispatch-24h/AGENT-3.md
```

### L1-4

```
AGENT L1-4 only. Import/swa-live-local: ignore LDI; APEX/INNER as clients; INSUDESIGN as service.
Grep UI for seed_demo, Smoke, Acme, lorem, fake@ — strip from client-visible path.
Never seed-demo. Report: work/reports/dispatch-24h/AGENT-4.md
```

### L1-5

```
AGENT L1-5 only. DELETE ZERO. git mv only.
KEEP: README.md, MEETING_AND_GO_LIVE_GUIDE.md, SUBMISSION.md, INSTALL_NO_IT.md,
DEPLOYMENT_CHECKLIST.md, handover USER_GUIDE + TRAINING_ONE_PAGER, ASSIGN-LEVELS.md.
SENT: SEND_IT / SEND_VIRAJ / REPLY_VIRAJ. STUBS: DEMO_SCRIPT, VIRAJ_TRIAL, JAYDEEP_MEETING_TODAY.
Archive other duplicate meeting/handoff/dispatch md to docs/historical/.
Write DOCS_MAP.md + AGENT-5.md. No third meeting file.
```

### L1-6

```
AGENT L1-6 only. Edit deliverables/MEETING_AND_GO_LIVE_GUIDE.md in place. Never fork.
Keep Jaydeep 12-min at TOP. Extra click script below. Share app not markdown.
Report: work/reports/dispatch-24h/AGENT-6.md
```

---

# LEVEL 2 — rest of the sidebar

**Gate:** Level 1 reports exist. **Done when:** AGENT-7.md … AGENT-12.md exist.

### L2-7 … L2-12 — paste SHARED + this

**L2-7:** 5 roles × CORE+Invoices+Users → 200/403/hidden/broken. Fix visible-button vs API 403. Report AGENT-7.md  

**L2-8:** Files/drawings: wire `/api/projects/{id}/documents` **or hide nav**. No fake page. Report AGENT-8.md  

**L2-9:** Tasks, Compliance (NBC/ECBC/IGBC/IS save), Sustainability (no hang), Users admin. Wire or remove. AGENT-9.md  

**L2-10:** Vendors, Materials, RFQs, Reports, BOQ/Quotes: wire or remove. Vendor /edit 404. AGENT-10.md  

**L2-11:** Time edit/delete; invoice-from-time UI; inquiry PM edit; convert `detail.candidates`. AGENT-11.md  

**L2-12:** Python 3.11 coverage honest; Playwright login→inquiries or NOT MEASURED. AGENT-12.md

---

# LEVEL 3 — meetings 1+2 rules still missing

**Gate:** L2. **Source:** `resources/MEETINGS_MASTER.md` (do not reopen locked WhatsApp).

Viraj: *match existing Excel logic, don’t invent a better process.*

| ID | Job |
|---|---|
| **L3-A** | Convert rule: inquire → if converts, **search client by name** → exist: add Project; else add Client then Project. Duplicate names → picker, not silent first-match |
| **L3-B** | SA = **yearly retainer** per client, not per-project. Tokens = units under that SA. UI copy must say this |
| **L3-C** | DBR/KDR **shared counter** (KDR id may be `…-DBR-00N`, type stays KDR). Other types free-text. Project required, token optional |
| **L3-D** | Time + doc-ref **may be non-project** (R&D/marketing dropped from MVP — nullable project is enough; don’t build marketing UI). Sustainability = **after** project completes |
| **L3-E** | Five MVP modules only in the story: Inquiries, Clients, SA, Tokens, Projects + DocRef + Time. Don’t pitch BOQ/vendor as the product |

---

# LEVEL 4 — folders: merge / archive / compact

**Gate:** L3. **Delete zero.** `git mv` only.

| ID | Job |
|---|---|
| **L4-A** | CURRENT docs only: README, MEETING_AND_GO_LIVE_GUIDE, SUBMISSION, INSTALL_NO_IT, DEPLOYMENT_CHECKLIST, handover USER_GUIDE + TRAINING_ONE_PAGER, ASSIGN-LEVELS.md. Everything else duplicate meeting/handoff → `docs/historical/` (already huge — don’t add more current) |
| **L4-B** | `work/DISPATCH-PLAN.md`, `PROFESSIONAL-GRADE-PLAN.md`, extra WORKER_PROMPT if unused → historical. Wave briefs stay. |
| **L4-C** | Frontend: one page per route; unused components (`TimesheetView` if dead) remove from nav not from git history |
| **L4-D** | Backend files >>300 lines you **already touch**: split by concept. Don’t mass-rewrite the tree |
| **L4-E** | DOCS_MAP update: path \| current \| archived \| sent-historical |

---

# LEVEL 5 — Excel sheets vs product

**Gate:** L4. **Source:** `resources/EXCEL_SHEETS_INVENTORY.md`, `docs/REAL_DATA.md`.

| ID | Job |
|---|---|
| **L5-A** | Core sheets import: Inquiries, Clients, SA, Tokens, Document Reference, Time, Sustainability. Row report. Ignore First Lead ID |
| **L5-B** | Project Tracking empty sample → projects from convert (already). Don’t fake tracking rows |
| **L5-C** | Independent sheets (HR, Finance, Complaints, Marketing, Bangalore/Western if dropped) → **do not import into MVP**. Document skip in importer |
| **L5-D** | APEX/INNER as **names** if they appear in live files later; INSUDESIGN as service_name. No enum of 4 SA types |

---

# LEVEL 6 — security + RBAC (Meeting access matrix)

**Gate:** L5.

| ID | Job |
|---|---|
| **L6-A** | Role matrix vs `docs/flows/02_auth_rbac.md` + code. Viewer read-only. Admin not blocked by project-membership IDOR |
| **L6-B** | JWT logout / token_version (users.token_version vs version). Refresh rotation — fix or NOT MEASURED |
| **L6-C** | `/metrics` auth (BACKLOG SF-4). Export job ownership (0035). documents write roles |
| **L6-D** | Audit log on convert, SA create, invoice send/paid |

---

# LEVEL 7 — ops (Jaydeep’s box, later)

**Gate:** L6. **Do not invent hostname/ports.**

| ID | Job |
|---|---|
| **L7-A** | `docs/INSTALL_NO_IT.md` + `DEPLOYMENT_CHECKLIST.md`: Windows Server, **free Docker Engine** (not paid Desktop unless they have it), WSL2, compose, secrets, healthz |
| **L7-B** | Backup: `make backup-db` / `backup-files`; daily DB / weekly files as Meeting 2 asked. Restore dry-run or NOT MEASURED |
| **L7-C** | Storage: local `uploads/` default; MinIO only if `STORAGE_BACKEND=minio`. Don’t force MinIO on laptop demo |
| **L7-D** | Celery/async export: wire a UI hook **or** document backend-only in meeting limits. No fake progress bar |

---

# LEVEL 8 — quality seal

**Gate:** L7.

| ID | Job |
|---|---|
| **L8-A** | Full pytest on **Python 3.11** + Postgres. Paste. Redis-down tests → environmental, not fake pass |
| **L8-B** | vitest coverage table. funcs<60% = BELOW THRESHOLD + add tests for L1 UI, don’t fake |
| **L8-C** | Playwright: login → INQ list → SA-011 visible or NOT MEASURED |
| **L8-D** | `alembic heads` single; 0036 applied |

---

# LEVEL 9 — internship / submission honesty

**Gate:** L8.

| ID | Job |
|---|---|
| **L9-A** | `deliverables/SUBMISSION.md` + README: replace stale “thresholds met”. Paste L8 numbers |
| **L9-B** | TECHNICAL_REPORT: Excel chain + GST + RBAC. No 572-without-paste |
| **L9-C** | ACTIVE.md wave-49/50/51 → real reports or NOT MEASURED |

---

# LEVEL 10 — dress rehearsal (ultimate before Jaydeep)

**Gate:** L9. **No new features.**

| ID | Job |
|---|---|
| **L10-A** | `make swa-live-local`. 12-minute script in MEETING_AND_GO_LIVE_GUIDE top. Screenshot/list IDs: INQ-001/003, SA-011+INSUDESIGN, TKN-001..004, CON/DBR/CAS/GAD |
| **L10-B** | Confirm 8 questions + locked answers + honest limits (laptop, freeze pending, no client-box load test, Files stub if still hidden) still in the guide |
| **L10-C** | Push **only if user says**: grouped commits, not `git add -A` |
| **L10-D** | One-page status for Srujan: DONE / BLOCKED (who) / don’t show |

**Level 10 done** = you can screen-share `:3100` tomorrow without dummy data and without opening dead pages.

---

## Missed-work rule (why 10 levels)

If an agent finds a hole **below** their level, they note it in the report as `DEFER L#` — they do not jump levels. You start that level next.

## After any level

Say **level N done, monitor** if you want Grok to only read reports + git status.  
Do not ask Grok to execute the ladder unless you explicitly say **run level N**.
