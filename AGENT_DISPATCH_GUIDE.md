# AGENT DISPATCH GUIDE — SWA ERP Final Submission

**Run each section in a SEPARATE terminal window/tab.**
**In each terminal: first run `/skill <name>`, THEN paste the prompt.**

---

## TERMINAL 1 — Backend Security Audit (`review-security`)

```bash
cd /Users/srujansai/Desktop/swa-erp
# In opencode: type "/skill review-security" then paste prompt below
```

**PROMPT:**
```
You are a backend security auditor. Use ONLY the review-security skill.

TARGET: /Users/srujansai/Desktop/swa-erp/src/backend

AUDIT THESE (produce PASS/FAIL/NOT_MEASURED with file:line evidence):
1. JWT rotation + refresh revocation (token_version) — auth_service.py, security.py
2. Refresh token reuse after logout — security.py:60-95
3. Access token valid after logout — security.py:26-39, deps.py:27-31
4. IDOR on /api/jobs/{id} — jobs.py:13-64 (ownership via user_has_project_access)
5. IDOR on /api/documents/{id} — documents.py:99-107,181-195 (project membership)
6. File upload containment — storage.py:42-62 (resolve + root check)
7. Rate limiting — rate_limit.py:24-48 (in-memory, DISABLE_AUTH_RATE_LIMIT kill-switch)
8. /metrics auth — main.py:111-113 (METRICS_REQUIRE_AUTH flag)
9. Input validation — BOQ parse (boq_service.py:40-58), file upload size limits
10. Money handling — Decimal(18,2), GST from settings, invoice numbering via sequence

OUTPUT: markdown with PASS/FAIL/NOT_MEASURED per item, file:line refs, top 5 critical findings.
```

---

## TERMINAL 2 — Frontend Quality Review (`review`)

```bash
cd /Users/srujansai/Desktop/swa-erp
# In opencode: type "/skill review" then paste prompt below
```

**PROMPT:**
```
You are a frontend quality reviewer. Use ONLY the review skill.

TARGET: /Users/srujansai/Desktop/swa-erp/src/frontend

REVIEW THESE (PASS/FAIL/NOT_MEASURED with file:line):
1. Coverage thresholds ENFORCED in vite.config.ts (stmts≥60, branch≥50, funcs≥60, lines≥60)
2. NO raw Number() for INR — central formatINR() using toLocaleString('en-IN')
3. NO naive Date()/toISOString().slice() — all display via formatIST() with Asia/Kolkata
4. NO hardcoded page_size:100 — all lists paginated; totals from API not sliced array
5. JWT in httpOnly cookie (not localStorage) — lib/auth.ts, lib/api.ts
6. Refresh rotation on 401 — lib/api.ts:137-142
7. Role-based route guards — ProtectedRoute.tsx exact match vs hierarchy
8. Dead UI — NO orphan pages (Vendors/RFQs/Materials/Tasks not in core flow)
9. A11y — aria-labels, focus-visible, keyboard nav, color contrast
10. Bundle — React.lazy code-splitting, manualChunks in vite.config, no 725KB single bundle

OUTPUT: markdown with PASS/FAIL/NOT_MEASURED per item, file:line refs, top 5 findings.
```

---

## TERMINAL 3 — Test Suite Integrity (`review-bugbot`)

```bash
cd /Users/srujansai/Desktop/swa-erp
# In opencode: type "/skill review-bugbot" then paste prompt below
```

**PROMPT:**
```
You are a test integrity engineer. Use ONLY the review-bugbot skill.

TARGET: /Users/srujansai/Desktop/swa-erp/tests + /Users/srujansai/Desktop/swa-erp/src/frontend

FIX THESE (produce exact commands run + results):
1. Run full backend suite on Python 3.11 + Postgres → exact pass/fail/skip counts
2. Identify flaky tests (run 3× each; mark flaky if any inconsistency)
3. Fix pytest-asyncio version mismatch (repo pins 8.3.3/0.24.0; env has 9.0.3/1.3.0)
4. Frontend: vitest --coverage thresholds 60/50/60/60 ENFORCED in vite.config.ts
5. Add skipif for Redis-dependent tests with self-explaining reason
6. Ensure CI runs full suite with Docker (postgres+redis+minio) and fails on any failure
7. Fix scripts/generate_metrics.sh if broken; run it and validators

OUTPUT: JSON { "backend": {...}, "frontend": {...}, "flaky": [...], "ci_green": bool, "commands_run": [...] }
```

---

## TERMINAL 4 — Docs & Metrics Reconciliation (`graphify`)

```bash
cd /Users/srujansai/Desktop/swa-erp
# In opencode: type "/skill graphify" then paste prompt below
```

**PROMPT:**
```
You are the docs truth officer. Use ONLY the graphify skill.

TARGET FILES (reconcile ALL numbers to fresh command output):
- README.md
- deliverables/SUBMISSION.md
- deliverables/TECHNICAL_REPORT.md
- HANDOFF.md
- work/ACTIVE.md
- plan/EXECUTION.md
- CHANGELOG.md
- work/reports/FINAL-CLOSE.report.md

RUN THESE FRESH (paste output):
- Frontend: npx vitest run --coverage (stmts/branch/funcs/lines)
- Backend static: ruff/black/mypy (clean)
- Alembic: alembic -c src/backend/alembic.ini heads
- Backend suite: ONLY if Docker available → else NOT MEASURED
- Load: wave-35 numbers only (dev machine)

RULES:
- REPLACE stale numbers (65.86%, 572, 523, 725KB, 0036) with fresh
- Mark Docker-dependent as NOT MEASURED with reason
- Open RISKs stay open; closed ones get commit hashes
- HALL_OF_SHAME: add entry if any stale claim found

OUTPUT: git diff for each file + reconciliation log.
```

---

## TERMINAL 5 — CI/CD & DevOps Gates (`create-hook`)

```bash
cd /Users/srujansai/Desktop/swa-erp
# In opencode: type "/skill create-hook" then paste prompt below
```

**PROMPT:**
```
You are the CI/CD engineer. Use ONLY the create-hook skill.

TARGET: /Users/srujansai/Desktop/swa-erp/.github/workflows + Makefile + Docker

CREATE THESE HOOKS/GATES:
1. pre-commit: ruff + black + mypy (backend) + tsc + eslint (frontend)
2. pre-push: vitest --coverage (thresholds) + pytest (if Docker)
3. ci.yml: ruff, black, mypy, pytest (Docker), tsc, eslint, vitest (thresholds), vite build
4. test.yml: full suite against Docker services (postgres:15, redis:7, minio)
5. Migration gate: alembic upgrade head + alembic check (single head)
6. pytest version lock: requirements.txt pytest==8.3.3 pytest-asyncio==0.24.0
7. Makefile: swa-live-local, migrate-data (dry-run default), backup-db, restore-db
7. Secrets: no hardcoded secrets; SECRET_KEY from env; SENTRY_DSN optional

OUTPUT: Modified workflow files + hooks.json + preflight script + verification run logs.
```

---

## TERMINAL 6 — Architecture & Code Hygiene (`create-rule`)

```bash
cd /Users/srujansai/Desktop/swa-erp
# In opencode: type "/skill create-rule" then paste prompt below
```

**PROMPT:**
```
You are the architecture janitor. Use ONLY the create-rule skill.

TARGET: /Users/srujansai/Desktop/swa-erp/src

CREATE ENFORCEABLE RULES FOR:
1. One file = one concept; max 300 lines
2. Explicit return types on all exports (TS) / type hints required (Python)
3. Dead code removal: unused exports, orphan pages, dead endpoints, unused imports
4. Import hygiene: absolute imports, no circular, group stdlib/third-party/local
5. Naming: PascalCase components, camelCase hooks/utils, snake_case Python
6. Error handling: no bare except; typed errors; structured logging (structlog)
7. Pydantic v2 for all schemas; SQLAlchemy 2 declarative; Alembic for every schema change
8. Split large PRs: each logical fix = own PR (max 300 lines changed)

OUTPUT: .cursor/rules/*.mdc files + list of files to delete/modify + PR split plan.
```

---

## TERMINAL 7 — Governance Loop (`loop`)

```bash
cd /Users/srujansai/Desktop/swa-erp
# In opencode: type "/skill loop" then paste prompt below
```

**PROMPT:**
```
You are the daily governance loop. Use ONLY the loop skill.

TARGET: /Users/srujansai/Desktop/swa-erp

CREATE A RECURRING LOOP (every 4 hours until meeting):
1. git pull origin main → rebase local
2. Run preflight: ruff + black + mypy + tsc + eslint → fail if any red
3. Run frontend: npx vitest run --coverage → fail if thresholds not met
4. If Docker available: run backend pytest → fail if any failure
5. Reconcile docs: grep for stale numbers (65.86, 572, 523, 725, 0036) → fix
6. Push to origin/main with commit: "chore: governance sync $(date -u +%Y-%m-%d)"
7. If any failure: create GitHub issue with logs

SCHEDULE: every 4 hours via cron or GitHub Actions schedule.
STOP CONDITION: meeting day — final seal only.

OUTPUT: GitHub Actions workflow .github/workflows/governance.yml + cron entry.
```

---

## QUICK VERIFICATION (run after all agents report)

```bash
cd /Users/srujansai/Desktop/swa-erp

# 1. All static gates green
ruff check src/backend/ && python3 -m black --check src/backend/ && python3 -m mypy src/backend/ --explicit-package-bases
cd src/frontend && npx tsc --noEmit && npx eslint . --ext ts,tsx --max-warnings 0 && npx vitest run --coverage

# 2. Frontend thresholds met
# Statements ≥60% | Branches ≥50% | Functions ≥60% | Lines ≥60%

# 3. Backend suite (if Docker available)
docker compose up -d postgres redis minio && python3 -m pytest tests/ -q --tb=no

# 4. Docs reconciled
grep -r "65.86\|572\|523\|725\|0036" README.md deliverables/SUBMISSION.md HANDOFF.md work/ACTIVE.md plan/EXECUTION.md CHANGELOG.md work/reports/FINAL-CLOSE.report.md 2>/dev/null || echo "CLEAN"

# 6. Push final
git push origin main
```