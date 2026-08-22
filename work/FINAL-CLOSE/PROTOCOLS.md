# Close Protocols P01–P20

Each protocol is **executable**. Output = evidence. No protocol is “done” without the listed proof.

Legend: **R** = read-only, **W** = write allowed, **G** = git commit expected.

---

## P01 — Grounding gate (R)

**When:** Session start, every resume.  
**Do:**
1. `git rev-parse HEAD` and `git status -sb`
2. Read `work/FINAL-CLOSE/README.md` + `ULTIMATE-CLOSE-GUIDE.md` §1
3. Read `work/reports/COMPLETION-HANDOFF-VERDICT.md` (if present)
4. Confirm waves 37/38 reports absent (or present if resuming mid-close)

**Pass:** Print HEAD, dirty files, which phase you will execute next.  
**Fail:** If unrelated dirty work exists — stop and ask human; don’t mix.

---

## P02 — Anti-fabrication oath (R)

**When:** Before any report or README metric.  
**Do:** Read `ANTI-FABRICATION.md` aloud into the session notes (summary is enough).  
**Pass:** You list 5 forbidden claims for this session.  
**Fail:** Claiming pass counts from memory.

---

## P03 — Sync ACTIVE.md (W, G)

**When:** Phase 1.  
**Do:** Update `work/ACTIVE.md` wave table:
- 32, 33, 34, 35, 36, 39 → **SHIPPED** (36 note: task-01 report missing; 02 exists)
- 37, 38 → **QUEUED** until done, then SHIPPED
- Remove “wave-36 report lost / dir missing” if `work/reports/wave-36/02-…` exists

**Pass:** Table matches git reality. Commit: `docs(active): sync waves 32-39 status for final close`

---

## P04 — Sync HANDOFF + EXECUTION + CHANGELOG (W, G)

**When:** Phase 1 (and rewrite again in Phase 5).  
**Do:**
1. `HANDOFF.md` — replace “PROJECT COMPLETE v1.0.1 only” with: product complete + professional-grade close in progress/done; point to FINAL-CLOSE pack
2. `plan/EXECUTION.md` — add rows for waves 32–39 status (or pointer to ACTIVE.md as SoT)
3. `CHANGELOG.md` `[Unreleased]` — note CI real gates, coverage, frontend tests, load, observability, repo org

**Pass:** A new session reading only HANDOFF would not think work stopped at Aug 11.  
**Commit:** `docs(handoff): reflect professional-grade close track`

---

## P05 — Fix 401-vs-403 standing failures (W, G)

**When:** Phase 2.  
**Targets:**
- `tests/wave-22/test_rbac_gaps.py::TestMaterialsAuth` (3)
- `tests/wave-4/test_task_assignments.py::test_assign_unauthorized`
- `tests/wave-8/test_reports_api.py::test_unauthorized_401`

**Decision (recommended):** Assert **403** when no `Authorization` header — matches FastAPI `HTTPBearer` default. Document in report. Do **not** change production auth to 401 just to please old tests unless you have a product reason.

**Pass:**
```bash
python3 -m pytest tests/wave-22/test_rbac_gaps.py tests/wave-4/test_task_assignments.py tests/wave-8/test_reports_api.py -q
# 0 failed
```
**Commit:** `test: align unauthenticated assertions with HTTPBearer 403`

---

## P06 — Solo full backend verify (R → append evidence)

**When:** After P05; again after wave-37 fixes.  
**Do:** Ensure no other pytest. Then:
```bash
python3 -m pytest tests/ -q --cov=src/backend --cov-report=term
```
**Pass:** 0 failed; TOTAL ≥85%; paste `task_service`, `notification_service`, `pdf_service`, `quote_service`, `import_service` lines.  
**Fail:** Concurrent DB chaos — stop, kill other runners, retry once.

---

## P07 — Fix TaskCard IST flake (W, G)

**When:** Phase 2.  
**Root cause:** `toISOString()` uses UTC; local IST can be next calendar day.  
**Fix options (pick one, prefer product correctness):**
1. Format due dates with local Y-M-D in the component/helper
2. Or freeze time in the test with a timezone-stable API

**Pass:**
```bash
cd src/frontend && npx vitest run src/components/tasks/__tests__/TaskCard.test.tsx
```
**Commit:** `fix(frontend): stabilize TaskCard overdue day across timezones`

---

## P08 — Frontend coverage verify (R)

**When:** After P07.  
```bash
cd src/frontend && npx vitest run --coverage && npx tsc --noEmit && npx eslint . --ext ts,tsx --max-warnings 0
```
**Pass:** 0 failed; thresholds ≥60/50/60/60. Record actual %.  
**Forbidden:** Copying 65.86% from old report without re-run.

---

## P09 — Wire Vitest into CI (W, G) [recommended]

**When:** Phase 2.  
**Do:** Add a job or step in `.github/workflows/ci.yml` under frontend:
```yaml
- run: npm ci
- run: npm run lint
- run: npx tsc --noEmit
- run: npx vitest run
- run: npm run build
```
(Adjust to existing script names.)

**Pass:** File changed; locally `npx vitest run` green.  
**Commit:** `ci: gate frontend unit tests with vitest`

---

## P10 — Fix Viraj architecture overview lies (W, G)

**When:** Phase 1 or 2.  
**File:** `deliverables/handover/ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md`  
**Change:** MinIO is implemented via `StorageBackend` (opt-in); Celery workers are wired (wave-31). Keep plain language. Point deploy questions to existing SEND_IT / INSTALL_NO_IT without re-asking.

**Pass:** Grep file for “not built” / “not yet wired” → 0 hits referring to MinIO/Celery.  
**Commit:** `docs: correct MinIO/Celery status in Viraj architecture overview`

---

## P11 — Wave-37 Phase 1 reviews (R)

**When:** Phase 3 start. Brief: `work/wave-37/01-independent-review.md`  
**Do:** Run all 7 tools listed. Deduplicate findings into a scratch table.  
**Pass:** List tool → scope → count of raw findings. Missing tool = documented skip, not silent.

---

## P12 — Wave-37 Phase 2 triage (R/W notes)

**When:** After P11.  
**For each finding:** CONFIRMED BUG | RISK | FALSE POSITIVE + reason.  
**Always include parked items:** 401/403 (if not fixed in P05), TaskCard, priority map triple, `/metrics` auth.  
**Pass:** Triage table complete; zero unexplained dismissals.

---

## P13 — Wave-37 Phase 3 fixes (W, G)

**When:** After P12.  
**Rule:** Only CONFIRMED BUGs. TDD: failing test first.  
**Pass:** Each fix has a test; suite still green (P06 + P08).  
**Commit:** one logical commit per bug or a small batch with clear message.

---

## P14 — Wave-37 report (W, G)

**Path:** `work/reports/wave-37/01-independent-review.report.md`  
**Must include:** tools run, triage table, fixes with before/after evidence, deferred RISKs, pasted suite summary.  
**Commit before** declaring wave-37 done.  
**Pass:** Report exists on `main` (or branch ready to merge).

---

## P15 — Consolidate priority maps (W, G) [if triage CONFIRMED or cleanup RISK accepted]

**File:** `src/backend/db/repositories/task_repo.py`  
**Do:** Single `_priority_map` used by list filter, update, and create.  
**Pass:** Tests for priority update/list still pass.  
**Commit:** `refactor: single priority map in task_repo`

---

## P16 — Optional wave-36-01 reconstruction (W, G)

**When:** If time; else document “superseded by 02 + code.”  
**Path:** `work/reports/wave-36/01-observability.report.md`  
**Pass:** Checklist from `work/wave-36/01-observability.md` marked with evidence pointers to code + 02 report.

---

## P17 — Wave-38 showcase docs (W, G)

**Brief:** `work/wave-38/01-submission-package.md`  
**Create/update:**
- `README.md` (evaluator front door)
- `docs/ARCHITECTURE.md` (mermaid; mark built vs target)
- `deliverables/TECHNICAL_REPORT.md`
- `deliverables/SUBMISSION.md` (refresh numbers from 32–37 reports only)
- `deliverables/DEMO_SCRIPT.md`

**Forbidden claims:** see ANTI-FABRICATION.md  
**Pass:** Every metric has `work/reports/...` citation.

---

## P18 — Wave-38 claim audit (R)

**Do:** Grep README + SUBMISSION + TECHNICAL_REPORT for percentages and pass counts. Cross-check each against a report file.  
**Pass:** Audit table in the wave-38 report. Any orphan number → remove or re-measure.

---

## P19 — Wave-38 report (W, G)

**Path:** `work/reports/wave-38/01-submission-package.report.md`  
**Pass:** Lists every claim → source. Commits landed. Suite still green.

---

## P20 — Close seal (W, G)

**Do:**
1. Write `work/reports/FINAL-CLOSE.report.md` (HEAD, date, phases, commands, external blockers)
2. Final `HANDOFF.md` + `ACTIVE.md` (37/38 SHIPPED)
3. Push `origin/main`
4. Optionally note “no new version tag required unless human wants v1.1.0 for evidence track”

**Pass:** Human can open FINAL-CLOSE.report.md and believe the project is engineering-closed in &lt;3 minutes.
