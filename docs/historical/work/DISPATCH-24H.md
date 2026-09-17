# MASTER PROMPT — one lane, 24 hours, Jaydeep tomorrow

**This file replaces prior dispatch drafts. Do not fork it.**

Integrator owns the seal. Agents do one workstream each. **No new variant files.** Edit what exists. Archive (`git mv` → `docs/historical/` or `attic/`) never delete.

---

## 0. FRAME (NON-NEGOTIABLE)

Real production ERP for **SWA Consultancy**. Client: **Viraj Shah**. Coordinator: **Jaydeep Varu**. Replaces ~20 live Excel sheets. Daily business. **₹50K only if it really works.**

NOT a demo, dummy site, portfolio, or college assignment.

- No fake data, dummy records, hardcoded mocks, dead buttons, or “coming soon” on anything the client can see.
- Every flow: real API, real Postgres, real `SWA-YYYY-XXX` IDs.
- Meeting: CEO / CFO / technical. You cannot fool them.

---

## 1. SITUATION

- Product **v1.0.1**. Waves 1–51 marked SHIPPED in docs (numbers may be stale).
- Meeting **TOMORROW** (~24 hours).
- Read `work/HANDOFF-2026-09-17.md` then **this file wins** on conflict.
- Meeting scripts (do not add a third):
  - `deliverables/JAYDEEP_MEETING_TODAY.md` (one page)
  - `deliverables/MEETING_AND_GO_LIVE_GUIDE.md` (full click — **refine, never fork**)
- Previous agents cluttered the tree. **Stop scattered mode.**

---

## 2. LOCKED — DO NOT REOPEN / “IMPROVE” / RE-ASK

WhatsApp 11/08/26 + 17/09/26:

1. **APEX / INNER** = client names. **INSUDESIGN** = service name. Not a 4th SA type.
2. **Yearly ID reset everywhere:** `SWA-2025-SA-011` → `SWA-2026-SA-001`. Already how counters work — don’t change the policy.
3. **Lead ID / LDI gone** even historically. Excel “First Lead ID” ignored. No Leads module.
4. **Flow:** Inquiry → Client → Project → Service Agreement → Token → Document Reference → Time Log → Invoice/GST → Compliance + Dashboard. RBAC.
5. **Server Qs** (Docker, WSL2, ports) = ask at the meeting. Do not block coding on them.

**Chat path (do not re-send SEND_IT / SEND_VIRAJ):**
Jun 26 Vikrant/IT intro → Aug 5 silent → Aug 11 three data Qs answered + “no IT dept” → Lead ID delete locked → Sep 15 check-in → Sep 17 Viraj “No 🙂” tagged Jaydeep “Yeah, I’ll see” → meeting **tomorrow**.

**Still on them:** Windows Server access, Excel freeze, import owner, first users. Not new modules.

---

## 3. FIX THESE (10% trash → 100% valuable)

1. **Dead buttons / half features** — click-through every screen. Fix or remove.
2. **Dummy data on the product surface** — purge. Fixtures only in tests.
3. **Bloat / folder junk / inconsistent UX** — clean. No new design system.
4. **Duplicate markdown** — merge. REPLACE never append. ARCHIVE never delete.
5. **Stale numbers** — frontend functions **58.45% < 60%**. Never say “thresholds met” without a fresh paste. NEVER fabricate. Else **NOT MEASURED**.
6. **Dirty tree** — `git status` + `git diff` FIRST. Do not blindly commit/revert. Another worker was in this tree.
7. **Unpushed `main`** — push only after a conscious freeze (end of 24h, integrator).
8. **Waves 49/50/51 reports** — real paste or NOT MEASURED. Fix `ACTIVE.md` links. `git log -S fresh_session_factory`.
9. **Env:** Docker **dead**. Local Postgres. Project **Python 3.11** (machine may be 3.14 — say so).

---

## 4. VERIFY BEFORE “DONE”

- Fresh suite on **3.11** + Postgres. One pytest at a time (`swa_erp_test`).
- Never trust a report — rerun.
- E2E: Inquiry → … → Invoice/GST → Compliance/Dashboard. Roles.
- UI: buttons, links, validation, empty, error.
- Reseal numbers. Commit only with user-aware freeze. Push last.

Live path: `make swa-live-local` — **never** `seed-demo` for SWA.  
UI **http://127.0.0.1:3100** `admin@swa.co.in` / `admin123!`

---

## 5. DOCS — COMPACT SET ONLY

Keep (edit in place):

- `README.md`
- `deliverables/MEETING_AND_GO_LIVE_GUIDE.md`
- `deliverables/JAYDEEP_MEETING_TODAY.md`
- `deliverables/SUBMISSION.md`
- `docs/INSTALL_NO_IT.md` + `DEPLOYMENT_CHECKLIST.md`
- `deliverables/handover/USER_GUIDE.md` + `TRAINING_ONE_PAGER.md`
- `work/DISPATCH-24H.md` (this file)

Sent historical (do not re-blast): `SEND_IT.md`, `SEND_VIRAJ.md`, `REPLY_VIRAJ.md`  
Pointers only: `DEMO_SCRIPT.md`, `VIRAJ_TRIAL_SCRIPT.md`  
Everything else duplicate → `docs/historical/`. **Delete zero files.**

---

## 6. MEETING PACK (tomorrow)

1. Screen-by-screen live show list  
2. One-line open  
3. Questions: SERVER / DATA / PROCESS  
4. Locked answers (section 2)  
5. Honest limits: laptop, Excel freeze pending, no client-box load test  
6. Closing line  

Already written in `JAYDEEP_MEETING_TODAY.md` — **refine, don’t fork.**

---

## 7. WORKSTREAMS (parallel after integrator git-orients)

| ID | Job | Report |
|---|---|---|
| A | Backend correctness + tests | `work/reports/dispatch-24h/A.md` |
| B | Frontend buttons/flows/UX | `work/reports/dispatch-24h/B.md` |
| C | Data realism + Excel import | `work/reports/dispatch-24h/C.md` |
| D | Docs merge + missing reports | `work/reports/dispatch-24h/D.md` |
| E | Git hygiene (no blind push) | `work/reports/dispatch-24h/E.md` |
| F | Meeting pack (refine existing) | `work/reports/dispatch-24h/F.md` |

No new files outside `work/reports/dispatch-24h/` without integrator approval.

---

## 8. DEFINITION OF DONE

- [ ] Every client-visible button in the Excel chain works live **or** is removed  
- [ ] Zero dummy names on `:3100` after `swa-live-local`  
- [ ] Tests: fresh 3.11 paste **or** NOT MEASURED  
- [ ] Coverage stated honestly  
- [ ] Docs compact; junk archived  
- [ ] Dirty tree resolved **consciously**  
- [ ] Push only when integrator + user agree  
- [ ] Meeting pack ready  
- [ ] Status against this checklist  

**24h done** = Jaydeep 12-minute script works on `:3100` with their IDs.  
**Money done** = that flow daily after **their** server + freeze (not this 24h).
