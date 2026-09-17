# What you give your agents (THE only pack)

Grok does **not** do this work. You paste. After they finish, say **agents done, monitor**.

**Live files (do not create more):**

| File | Who uses it |
|---|---|
| **This file** | You → agents |
| `deliverables/MEETING_AND_GO_LIVE_GUIDE.md` | You tomorrow (Jaydeep 12 min at the top; extra click script below) |

**How:** Agent 1 first. Then 2–6 in parallel. Each paste = SHARED + their AGENT N only.  
Each writes **only** `work/reports/dispatch-24h/AGENT-N.md`.

---

## SHARED (every agent)

```
You work in /Users/srujansai/Desktop/swa-erp.

NOT A DEMO. Daily ERP for SWA Consultancy (Viraj Shah; Jaydeep Varu).
Replaces ~20 Excel sheets. ₹50K only if it really works. Meeting TOMORROW
with Jaydeep + possibly CEO/CFO/technical. No fake data, no dummy records,
no dead buttons, no "coming soon" on anything they can see.
No new frameworks, no new UI kit, no extra markdown variants, no *_v2.md.
Edit existing files. git mv to docs/historical/ or attic/ — NEVER delete.

Do ONLY your AGENT number. Do NOT commit unless the user says to commit
YOUR files. Do NOT push. Do NOT git add -A. Do NOT blindly revert.

FIRST:
  git status -sb
  git log --oneline -10
  git diff --stat

LOCKED (do not reopen):
1. APEX / INNER = client names. INSUDESIGN = service name. Not a 4th SA type.
2. Yearly IDs: SWA-2025-SA-011 → SWA-2026-SA-001 everywhere. Don't change policy.
3. Lead ID / LDI gone even historically. First Lead ID ignored on import. No Leads module.
4. Flow: Inquiry → Client → Project → SA → Token → Doc Ref → Time → Invoice/GST → Compliance + Dashboard.
5. Docker/WSL2/ports = ask tomorrow. Don't block on them.

NEVER claim: 100% complete, zero risk, server live, 100+ users on THEIR box,
"thresholds met" (frontend functions 58.45% < 60% until a FRESH Python 3.11
vitest paste). NEVER fabricate. Else NOT MEASURED.

make swa-live-local  (NEVER seed-demo)
http://127.0.0.1:3100  admin@swa.co.in / admin123!
http://127.0.0.1:8100/healthz
Python 3.11 (not 3.14). Docker DEAD. One pytest at a time (ps aux | grep pytest).

Meeting file (refine, never fork): deliverables/MEETING_AND_GO_LIVE_GUIDE.md
Report ONLY: work/reports/dispatch-24h/AGENT-N.md
```

---

## AGENT 1 — freeze + numbers (FIRST)

```
AGENT 1 only. You block 2–6 until done.

1. Split dirty files: meeting-critical vs other-worker. ASK user before commit.
   KEEP if present: AgreementsPage, TokensPage, InvoicesPage, DashboardPage,
   lib/api.ts, invoice_repo.py, inquiry_service.py, auth_service.py,
   alembic 0036_token_version_and_is_billed.py,
   deliverables/MEETING_AND_GO_LIVE_GUIDE.md, work/ASSIGN-TO-AGENTS.md
2. Python 3.11: pytest+cov; cd src/frontend && npx vitest run --coverage;
   ruff, black --check, mypy; tsc, eslint, vite build; alembic heads (one head).
3. Paste numbers table. If frontend funcs < 60%: BELOW THRESHOLD.
   Update README/SUBMISSION only with those numbers.
4. Wave 49/50/51 reports: this paste or NOT MEASURED. Fix work/ACTIVE.md links.
   git log -S fresh_session_factory — landed or NOT FOUND.

Report: work/reports/dispatch-24h/AGENT-1.md
```

---

## AGENT 2 — backend chain (after 1)

```
AGENT 2 only. Excel chain backend. No new modules.

Convert: New+Contacted; reuse or create client; always Project; yearly CLT/PRJ IDs.
SA: free-text service_name, INSUDESIGN valid.
Token under agreement.
Doc ref: project + doc_date; DBR/KDR share counter.
Time: 15-min, billable.
Invoice: Decimal 18,2 INR; GST 18% line; draft→sent→paid; sequence IF NOT EXISTS.
Import ignores First Lead ID / LDI.

Acceptance: python3 scripts/smoke_chain.py prints SWA- IDs, then tell user to
make swa-live-local (smoke pollutes).
Report: work/reports/dispatch-24h/AGENT-2.md
```

---

## AGENT 3 — frontend buttons (after 1)

```
AGENT 3 only. Wire or remove dead buttons. No new pages. Files/drawings stays stub.

:3100 after swa-live-local, admin:
New Inquiry; Convert INQ-003; Convert 300 uses detail.candidates;
New Agreement on Agreements list (INSUDESIGN); New Token on Tokens list;
New DBR; time 1.00h billable; invoice GST 18% not 1800%; Mark sent/paid;
delete 204 no JSON toast; dashboard not empty amber; no Smoke/Acme/lorem.

Click INQ-001/003, SA-011+INSUDESIGN, TKN-001..004, CON/DBR/CAS/GAD.
Report: work/reports/dispatch-24h/AGENT-3.md
```

---

## AGENT 4 — import + no dummy (after 1)

```
AGENT 4 only.
Import/swa-live-local: ignore LDI; APEX/INNER as clients; INSUDESIGN as service.
Grep UI for seed_demo, Smoke, Acme, lorem, fake@ — strip from client-visible path.
Never seed-demo.
Report: work/reports/dispatch-24h/AGENT-4.md
```

---

## AGENT 5 — docs archive (after 1)

```
AGENT 5 only. DELETE ZERO. git mv only.

KEEP: README.md, deliverables/MEETING_AND_GO_LIVE_GUIDE.md,
deliverables/SUBMISSION.md, docs/INSTALL_NO_IT.md, docs/DEPLOYMENT_CHECKLIST.md,
handover USER_GUIDE.md + TRAINING_ONE_PAGER.md, work/ASSIGN-TO-AGENTS.md.

SENT (do not re-blast): SEND_IT.md SEND_VIRAJ.md REPLY_VIRAJ.md
STUBS ok: DEMO_SCRIPT.md VIRAJ_TRIAL_SCRIPT.md (must point at MEETING_AND_GO_LIVE_GUIDE).
If JAYDEEP_MEETING_TODAY.md still exists as a full copy, git mv it to
docs/historical/deliverables/ — content is already in the meeting guide top.

Archive other duplicate meeting/handoff/dispatch md.
Write: work/reports/dispatch-24h/DOCS_MAP.md (path | current | archived | sent)
AND AGENT-5.md. No third meeting file.
```

---

## AGENT 6 — meeting file (after 1, parallel with 2–5)

```
AGENT 6 only. Edit deliverables/MEETING_AND_GO_LIVE_GUIDE.md in place. Never fork.

Keep the Jaydeep 12-min block at the TOP (show list, 8 questions, locked answers,
honest limits, close). Extra-time click script stays below. Share-app not markdown.
Report: work/reports/dispatch-24h/AGENT-6.md
```

---

## After they finish

Say to Grok: **agents done, monitor**
