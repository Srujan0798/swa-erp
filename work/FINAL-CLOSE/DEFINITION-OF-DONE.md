# Definition of Done — Engineering Close

You may tell the human **“the project is closed for internship submission”** only when **all** boxes below are true.

---

## A. Evidence track

- [ ] Wave-37 report on main with triage table + tool list
- [ ] Wave-38 report on main with claim→source audit
- [ ] `FINAL-CLOSE.report.md` written and truthful
- [ ] `ACTIVE.md` shows 32–39 SHIPPED (or 36 noted with missing 01)
- [ ] `HANDOFF.md` describes post-professional-grade close state

## B. Suites & gates

- [ ] `pytest tests/ -q` → **0 failed** (401/403 fixed)
- [ ] Backend coverage TOTAL ≥ **85%**
- [ ] Five targets still ≥70%: pdf, quote, import, task, notification services
- [ ] Frontend vitest → **0 failed** (TaskCard fixed)
- [ ] Frontend thresholds ≥60/50/60/60 on a **fresh** run
- [ ] `ruff`, `mypy`, `tsc`, `eslint` clean
- [ ] Vitest present in CI (recommended; if skipped, FINAL-CLOSE must say so explicitly)

## C. Submission surfaces

- [ ] README is evaluator-facing (not only orchestrator quick-start)
- [ ] Architecture doc has mermaid; built vs target marked
- [ ] TECHNICAL_REPORT includes requirements-misread story + limitations
- [ ] SUBMISSION metrics match wave reports
- [ ] DEMO_SCRIPT exists and is runnable against a local stack
- [ ] Viraj architecture overview no longer lies about MinIO/Celery

## D. Git

- [ ] All close commits on `origin/main`
- [ ] Working tree clean (or only known unrelated dirt called out)

## E. Honest external remainder (must be stated, not hidden)

- [ ] FINAL-CLOSE.report.md lists: Viraj server facts, deploy, Excel migration owner, client-box load test as **external**

---

## What “closed” does **not** mean

- Company production live on Windows Server  
- Zero RISKs in the wave-37 triage table  
- Every backend file ≥70% coverage  
- Client WhatsApp fully resolved  

If A–E are true and E is stated honestly → **CLOSED**.
