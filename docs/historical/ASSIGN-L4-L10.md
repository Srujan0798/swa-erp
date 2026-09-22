# PASTE TO YOUR AGENTS — Levels 4–10

Grok stopped the auto-loop (usage). You dispatch these **manually**.

**Already done (do not re-run):** L1 AGENT-1..6, L2 AGENT-7..12, L3-A + L3-C.  
**Still in flight if OpenCode is running:** L3-B, L3-D, L3-E — wait for those reports, **then** start L4.

Repo: `/Users/srujansai/Desktop/swa-erp`  
Model: `opencode/union-alpha`  
**One worktree per agent.** Never two writers on `swa-erp` main.  
Reports: `/Users/srujansai/Desktop/swa-erp/work/reports/dispatch-24h/AGENT-<ID>.md`

```
opencode run -m opencode/union-alpha --dir <WORKTREE> --title "L4-A" --auto "<SHARED + AGENT BLOCK>"
```

---

## SHARED (every agent L4–L10)

```
NOT A DEMO. SWA ERP. Viraj Shah / Jaydeep Varu. ₹50K only if it works.
LOCKED: APEX/INNER=clients; INSUDESIGN=service; yearly IDs; no LDI/Leads.
No new meeting files. No *_v2.md. git mv archive, NEVER delete.
Do NOT git add -A. Do NOT commit unless user says. Do NOT push.
Do NOT seed-demo. Python 3.11. One pytest at a time.
Never claim thresholds met without a fresh paste. Else NOT MEASURED.
Read work/ASSIGN-LEVELS.md. Do ONLY this AGENT id.
Write report to /Users/srujansai/Desktop/swa-erp/work/reports/dispatch-24h/AGENT-<ID>.md then STOP.
```

---

## LEVEL 4 — compact folders (after L3-B/D/E reports)

**L4-A**
```
L4-A. DELETE ZERO. git mv only.
KEEP current: README.md, deliverables/MEETING_AND_GO_LIVE_GUIDE.md, SUBMISSION.md,
docs/INSTALL_NO_IT.md, DEPLOYMENT_CHECKLIST.md, handover USER_GUIDE + TRAINING_ONE_PAGER,
work/ASSIGN-LEVELS.md, work/ASSIGN-L4-L10.md.
Archive duplicate meeting/handoff/dispatch md to docs/historical/.
Report AGENT-L4-A.md list of moves.
```

**L4-B**
```
L4-B. git mv work/DISPATCH-PLAN.md work/PROFESSIONAL-GRADE-PLAN.md unused WORKER_PROMPT
to docs/historical/work/ if they are unused templates. Wave briefs stay. Report AGENT-L4-B.md.
```

**L4-C**
```
L4-C. Frontend: one page per route. If TimesheetView is unused in nav, don't delete git history —
remove from Sidebar only. Report AGENT-L4-C.md.
```

**L4-D**
```
L4-D. Split backend files >>300 lines ONLY if you already touch them. No mass rewrite.
Report AGENT-L4-D.md.
```

**L4-E**
```
L4-E. Update work/reports/dispatch-24h/DOCS_MAP.md: path | current | archived | sent-historical.
Report AGENT-L4-E.md.
```

---

## LEVEL 5 — Excel vs product (after L4)

**L5-A**
```
L5-A. Import Inquiries, Clients, SA, Tokens, Document Reference, Time, Sustainability.
Ignore First Lead ID. Paste dry-run row counts. Report AGENT-L5-A.md.
```

**L5-B**
```
L5-B. Project Tracking sample was empty — projects come from convert. Do not fake rows.
Report AGENT-L5-B.md.
```

**L5-C**
```
L5-C. Do NOT import HR, Finance, Complaints, Marketing, Bangalore/Western into MVP.
Document skip in importer. Report AGENT-L5-C.md.
```

**L5-D**
```
L5-D. APEX/INNER = names if they appear. INSUDESIGN = service_name. No 4th SA type enum.
Report AGENT-L5-D.md.
```

---

## LEVEL 6 — security (after L5)

**L6-A**
```
L6-A. Role matrix vs docs/flows/02_auth_rbac.md. Viewer read-only. Admin not blocked by
project-membership IDOR. UserRead.email is str (import@swa.local). Report AGENT-L6-A.md.
```

**L6-B**
```
L6-B. JWT logout / users.token_version vs version column. Refresh rotation. Fix or NOT MEASURED.
Report AGENT-L6-B.md.
```

**L6-C**
```
L6-C. /metrics auth. Export job ownership (0035). documents write roles. Report AGENT-L6-C.md.
```

**L6-D**
```
L6-D. Audit log on convert, SA create, invoice sent/paid. Report AGENT-L6-D.md.
```

---

## LEVEL 7 — Jaydeep install paper (after L6)

**L7-A**
```
L7-A. Refine docs/INSTALL_NO_IT.md + DEPLOYMENT_CHECKLIST.md: Windows Server, free Docker Engine
(not paid Desktop), WSL2, compose, secrets, healthz. Do not invent hostname. Report AGENT-L7-A.md.
```

**L7-B**
```
L7-B. make backup-db / backup-files. Restore dry-run or NOT MEASURED. Report AGENT-L7-B.md.
```

**L7-C**
```
L7-C. Storage local uploads/ default. MinIO only if STORAGE_BACKEND=minio. Report AGENT-L7-C.md.
```

**L7-D**
```
L7-D. Celery/async export: real UI hook OR document "backend-only" in meeting limits. No fake bar.
Report AGENT-L7-D.md.
```

---

## LEVEL 8 — quality (after L7)

**L8-A**
```
L8-A. python3.11 pytest + Postgres. Paste. Redis-down = environmental not fake pass.
Backend full cov was NOT MEASURED (timeouts). Report AGENT-L8-A.md.
```

**L8-B**
```
L8-B. vitest --coverage. Last paste: functions 62.38% (580 tests). Re-run; paste table.
If funcs<60% BELOW THRESHOLD. Report AGENT-L8-B.md.
```

**L8-C**
```
L8-C. Playwright login → inquiries list → SA-011 or NOT MEASURED. Report AGENT-L8-C.md.
```

**L8-D**
```
L8-D. alembic heads single; 0036 applied. Report AGENT-L8-D.md.
```

---

## LEVEL 9 — submission honesty (after L8)

**L9-A**
```
L9-A. SUBMISSION.md + README: replace stale thresholds met. Paste L8 numbers. Report AGENT-L9-A.md.
```

**L9-B**
```
L9-B. TECHNICAL_REPORT: Excel chain + GST + RBAC. No 572-without-paste. Report AGENT-L9-B.md.
```

**L9-C**
```
L9-C. ACTIVE.md wave-49/50/51 → real reports or NOT MEASURED. Report AGENT-L9-C.md.
```

---

## LEVEL 10 — dress rehearsal (after L9)

**L10-A**
```
L10-A. make swa-live-local. Walk MEETING_AND_GO_LIVE_GUIDE top 12 min.
IDs: INQ-001/003, SA-011+INSUDESIGN, TKN-001..004, CON/DBR/CAS/GAD.
Report AGENT-L10-A.md. Never seed-demo.
```

**L10-B**
```
L10-B. Guide still has 8 questions, locked answers, honest limits
(laptop, Excel freeze, no client-box load test, Files unfinished). Report AGENT-L10-B.md.
```

**L10-C**
```
L10-C. Do NOT push unless user says. If they say yes: grouped commits, never git add -A.
Worktree merges (wt-l2-11 invoice-from-time, wt-l3-b SA copy) need user pick.
Report AGENT-L10-C.md.
```

**L10-D**
```
L10-D. One-page status: DONE / BLOCKED(who) / DON'T SHOW (Files/drawings, Vendors first).
Write work/reports/dispatch-24h/L10-D.md — this is the loop's DONE file.
```

---

## Status snapshot when Grok stopped

| Level | Status |
|---|---|
| 1 | Reports AGENT-1..6 |
| 2 | Reports AGENT-7..12. Code mostly in **worktrees**, not merged to `:3100` |
| 3 | A+C reports. B/D/E may still be running in `wt-l3-b/d/e` |
| 4–10 | **Not started.** Paste from this file |

**Tomorrow meeting (you):** `deliverables/MEETING_AND_GO_LIVE_GUIDE.md` + **http://127.0.0.1:3100**  
`admin@swa.co.in` / `admin123!` after `make swa-live-local`. Do not open Files/drawings.
