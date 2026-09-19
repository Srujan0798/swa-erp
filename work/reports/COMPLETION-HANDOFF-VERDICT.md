# Completion handoff — living verdict

**As of:** 2026-08-23 (pass 2 — clean coverage re-verify after `swa_erp_test` reset)  
**HEAD:** `4050f51` = `origin/main` (**pushed**; earlier “5 ahead” is resolved)  
**Untracked:** only this note (`work/reports/COMPLETION-HANDOFF-VERDICT.md`)  
**Purpose:** Brutal truth table for professional-grade waves 32–39 before writing Claude prompts.

---

## Truth table (waves 32–39)

| Wave | ACTIVE.md says | Git / reports reality | Verdict |
|---|---|---|---|
| **32** CI real gates | SHIPPED ✅ | Reports + gates on main | **SHIPPED** |
| **33** Backend coverage | **IN-FLIGHT** | Merged `4050f51`; report 03 on main; **independently re-verified** `5 failed / 557 passed / 1 skipped`, TOTAL **86%**, all 5 targets ≥70%, **all `services/*.py` ≥70%** | **SHIPPED (evidence solid). ACTIVE stale.** |
| **34** Frontend tests | **IN-FLIGHT** | Reports 01+02 on main; thresholds met independently (~61% stmts); **TaskCard flake under IST** | **SHIPPED with known flake.** ACTIVE stale |
| **35** Load validation | SHIPPED ✅ | `docs/PERFORMANCE.md` + `docs/performance-runs/` | **SHIPPED** |
| **36** Observability | **IN-FLIGHT**; “report lost” | Code on main; **`02-post-merge-fixes.report.md` exists**; **`01-observability.report.md` never existed in git** | **CODE SHIPPED.** Status/docs half-stale |
| **37** Independent review | QUEUED | Brief only; **not started** | **QUEUED — next engineering gate** |
| **38** Submission package | QUEUED | Brief only; depends on 32–37 | **QUEUED — after 37** |
| **39** Repo organization | **IN-FLIGHT** | Report COMPLETE; merged `prof-G` | **SHIPPED.** ACTIVE stale |

**Product v1.0.1 (waves 1–31):** shipped. Professional-grade track (32–39) is **not** “100% complete” — **37 and 38 remain**.

---

## Coverage — independently verified (2026-08-23)

### Backend (wave-33) — CLEAN RUN

Method: `DROP/CREATE swa_erp_test`, then  
`pytest tests/ -q --cov=src/backend --cov-report=term` via `/tmp/swa-erp-venv` (Python 3.11).  
Log: `/tmp/swa-clean-cov.txt`.

| Metric | Result |
|---|---|
| Suite | **5 failed, 557 passed, 1 skipped** (151.7s) |
| TOTAL | **8702 stmts, 1201 miss → 86%** |
| Failures | Same 5× 401-vs-403 (`wave-22` MaterialsAuth×3, `wave-4` assign_unauthorized, `wave-8` unauthorized_401) |

| Wave-33 target | Cover |
|---|---|
| `pdf_service.py` | **100%** |
| `quote_service.py` | **97%** |
| `import_service.py` | **80%** |
| `task_service.py` | **97%** |
| `notification_service.py` | **100%** |

**Services layer:** **0** of ~30 `services/*.py` modules are below 70%. Stronger than the 5-target brief.

**Global “no module below 70%” is FALSE** if taken literally over all of `src/backend` (incl. alembic). From the same dump: **32 modules &lt;70%**; **9 non-alembic**:

| Cover | Module |
|---|---|
| 0% | `core/exceptions.py`, `models/task_dependency.py`, `db/repositories/task_dependency_repo.py` |
| 34% | `core/boq_parser.py` |
| 41% | `api/quotes.py` |
| 47% | `db/repositories/notification_repo.py` |
| 52% | `api/notifications.py` |
| 63% | `api/agreements.py` |
| 69% | `api/tokens.py` |

**Submission-safe wording:** “Backend overall **86%**; all service modules ≥70%; wave-33 closed the five weakest services.” **Do not** say “no backend module under 70%.”

CI gate remains `--cov-fail-under=82` (Makefile) — 86% clears it; the aspirational 85% wave goal is also met.

### Frontend (wave-34)

| Source | Statements | Branches | Functions | Lines | Tests |
|---|---|---|---|---|---|
| Report 02 (claimed) | **65.86%** | 54.63% | 63.72% | 66.73% | 522 / 0 fail |
| Independent (`vitest --coverage`, excl. TaskCard) | **61.4%** | **51.25%** | **60.32%** | **62.19%** | 518 pass |
| Full suite incl. TaskCard (IST) | — | — | — | — | **521 pass, 1 fail** |

- Thresholds (**60/50/60/60**) **pass** on independent measurement.
- Cite **~61% stmts** (or re-run), not 65.86% (smaller denominator / older snapshot).

**TaskCard flake — root cause (reproduced):**
- Test: `fmt = (d) => d.toISOString().split("T")[0]` (UTC calendar date).
- Component: `new Date(dueDate + "T00:00:00")` (local).
- Under **Asia/Kolkata**, `setDate(-3)` local midnight → `toISOString()` yields **previous UTC day** → shows **4d overdue** vs expected **3d**.
- **Passes with `TZ=UTC`**, fails with `TZ=Asia/Kolkata` (and default local IST).
- Fix for wave-37: format due dates in local Y-M-D (not `toISOString`), or freeze clock / use UTC consistently in both test and component.

---

## ACTIVE.md vs git (stale rows)

`work/ACTIVE.md` (mtime still Aug 22) still marks 33/34/36/39 as IN-FLIGHT and says wave-36 report “does not exist.” Reality:

- **33, 34, 39:** flip to **SHIPPED** (33 now independently verified).
- **36:** code + `02-…report.md` present; mark **SHIPPED (task-01 report never written)**. Fix the “report lost / directory missing” note — directory exists.
- **37 / 38:** QUEUED — correct.
- **`HANDOFF.md`:** still “PROJECT COMPLETE: v1.0.1” (2026-08-11). **Dangerously stale** — omits waves 32–39.
- **`deliverables/SUBMISSION.md`:** still product v1.0.1 package; wave-38 must refresh metrics / professional-grade evidence.

**Push:** `origin/main` == `4050f51` ✅  

**prof-D worktree:** tip `9cb2b22`, fully merged; safe to prune.

---

## Waves 37 / 38 — what “complete” still means

### Wave-37 (independent adversarial review)
- Brief: `/Users/srujansai/Desktop/swa-erp/work/wave-37/01-independent-review.md`
- Depends on **32–35** (not 36). Those deps are effectively landed.
- Must run **7 review tools**, triage table, fix only CONFIRMED BUGs with failing-test-first.
- Known follow-ups already parked for it: consolidate triplicate `_priority_*` maps in `task_repo.py`; triage 5× 401-vs-403 tests; TaskCard date flake.
- **Not optional for an internship submission** — it is the credibility wave.

### Wave-38 (submission package)
- Brief: `/Users/srujansai/Desktop/swa-erp/work/wave-38/01-submission-package.md`
- Depends on **32–37**. Rewrites README, architecture diagrams, technical report, SUBMISSION metrics, demo script.
- Rule: **every metric traceable to a wave report**. Running early will bake in stale ACTIVE / inflated coverage.

---

## IT / server docs

| Artifact | Status |
|---|---|
| `deliverables/SEND_IT.md` | **Exists** — sendable 8-question brief for Vikrant/IT (or Viraj) |
| `docs/IT_BRIEF.md` | Pointer only → SEND_IT |
| `docs/decisions/0003-it-server-call-brief.md` | ADR context; still useful |
| `docs/INSTALL_NO_IT.md` | **Exists** — install path when there is **no IT dept** |
| Client fact (HANDOFF / SUBMISSION) | Viraj: **no IT department**; server facts still **OPEN** — deploy blocker |

Drafts for IT **exist**; answers **do not**. Product can be “engineering-complete” while **not company-server-live**.

---

## Recommended completion order

1. **Hygiene (minutes):** Update `ACTIVE.md` + `HANDOFF.md` to match verified state above. Optional: prune `prof-D` worktree. (Push already done.)
2. **Optional stabilize before/during 37:** Fix TaskCard local-date flake; resolve 5× 401-vs-403 (prefer assert 403 — matches FastAPI `HTTPBearer`).
3. **Ship wave-37** (adversarial review + triage + small fixes) — **deps 32–35 met.**
4. **Ship wave-38** (submission package from verified numbers only).
5. **Deploy path (external):** `SEND_IT.md` / `INSTALL_NO_IT.md` when Viraj has bandwidth.

---

## Draft Claude / agent prompt templates

*(Ready for when user picks a path — do not auto-dispatch.)*

### A — Status hygiene only
```
Update work/ACTIVE.md and HANDOFF.md to HEAD 4050f51 / origin/main.
Mark 32–36 and 39 SHIPPED; 37/38 QUEUED. Caveats: wave-36 missing task-01 report;
backend cite 86% overall + all services ≥70% (NOT "no module <70%" globally — 9
non-alembic modules still <70%, see work/reports/COMPLETION-HANDOFF-VERDICT.md);
frontend cite ~61% stmts. Do not touch src/. Commit docs only.
```

### B — Stabilize flakes (optional pre-37)
```
1) Fix TaskCard.test.tsx: stop using toISOISOString() for local calendar dates
   (or set TZ=UTC in vitest); prove green under TZ=Asia/Kolkata and TZ=UTC.
2) Change the 5 auth tests to expect 403 (or document why 401); suite should be
   0 failed on backend. Append note to wave-33 or wave-37 report. Small commits.
```

### C — Dispatch wave-37
```
Execute work/wave-37/01-independent-review.md exactly. Run all 7 tools listed.
Also triage: (a) 5× 401-vs-403, (b) TaskCard IST flake, (c) triplicate priority
maps in task_repo.py, (d) dead task_dependency* at 0% coverage — RISK or BUG?
No wave-38 docs. Report → work/reports/wave-37/01-independent-review.report.md
```

### D — Dispatch wave-38 (only after 37)
```
Execute work/wave-38/01-submission-package.md. Metrics must cite wave reports +
/tmp-style command output. Forbidden: "100% complete"; global "no module <70%";
frontend 65.86%. Allowed: backend 86%, services ≥70%, frontend ≥60% thresholds,
load-test from docs/PERFORMANCE.md. Refresh deliverables/SUBMISSION.md beyond v1.0.1.
```

### E — IT / deploy (non-code)
```
Do not invent server facts. Package deliverables/SEND_IT.md + docs/INSTALL_NO_IT.md
into a short WhatsApp/email for Viraj. Ask only the 8 questions. No architecture re-litigation.
```

---

## Bottom line

- **Not 100% complete.** Product v1.0.1 yes; waves **32–36 + 39 effectively shipped**; **37 and 38 remain**.
- **Coverage claims now independently locked:** backend **86% / 557+5+1**; services all ≥70%; global no-module-under-70 **false**.
- **Biggest immediate risk:** stale `ACTIVE.md` / `HANDOFF.md` → next session overclaims or redoes finished work.
- **Biggest engineering remaining work:** wave-37 review + wave-38 honest packaging.
- **Biggest external blocker:** server facts (no IT dept) — drafts ready, answers not.

---

## Execution pack (user-confirmed full close)

**Start:** [`work/FINAL-CLOSE/README.md`](../FINAL-CLOSE/README.md)  
**Paste to Claude:** [`work/FINAL-CLOSE/prompts/PASTE-TO-CLAUDE.md`](../FINAL-CLOSE/prompts/PASTE-TO-CLAUDE.md)  
**Human ops:** [`work/FINAL-CLOSE/HUMAN-PLAYBOOK.md`](../FINAL-CLOSE/HUMAN-PLAYBOOK.md)

Path locked: **hygiene → stabilize → wave-37 → wave-38 → seal**.
