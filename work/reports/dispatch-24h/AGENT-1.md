# AGENT-1 Report — Freeze + Numbers

## Test Results (Python 3.11 / pytest)

| Suite | Passed | Failed | Skipped | Notes |
|-------|--------|--------|---------|-------|
| migrations + wave-1 | 54 | 1 | 1 | `test_logout_revokes_refresh` fails (expects 401, gets 200) |

**Total backend tests run:** 56 (subset — full suite timed out at 300s)

## Coverage Numbers

### Backend (pytest --cov=src/backend)
```
TOTAL: 45% (8650 statements, 4747 missed)
```
Key service coverage:
- auth_service: 90%
- user_service: 83%
- import_service: 0% (excluded)
- export_service: 12%
- invoice_service: 26%
- inquiry_service: 32%

### Frontend (vitest --coverage)
| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Statements | 62.64% | — | — |
| Branches | 53.48% | — | — |
| **Functions** | **60.35%** | **≥60%** | **ABOVE** |
| Lines | 63.78% | — | — |

**Frontend function coverage: 60.35% — ABOVE 60% threshold (barely)**

## Lint / Type Gates

| Tool | Command | Result |
|------|---------|--------|
| ruff | `ruff check src/backend` | **PASS** |
| black | `python -m black --check src/backend` | **PASS** |
| mypy | `python -m mypy src/backend --explicit-package-bases` | **PASS** |
| tsc | `npx tsc --noEmit` | **FAIL** — 8 errors (unused vars, type mismatches in PnlDashboard test) |
| eslint | `npx eslint src` | **FAIL** — 3 errors (unused `userEvent`, `vi` in test files) |
| vite build | `npx vite build` | **PASS** |

## Database / Migrations

- `alembic heads` → **0036 (head)** — single head ✓

## Wave 49/50/51 Reports

| Wave | Report Location | Status |
|------|----------------|--------|
| 49 | `work/reports/wave-49/01-transaction-atomicity.report.md` | EXISTS |
| 50 | `work/reports/wave-50/02-deterministic-test-suite.report.md` | EXISTS (note: ACTIVE.md references `01-deferred-security-risks.md` which doesn't exist) |
| 51 | `work/reports/wave-51/` | **MISSING** — report at `work/wave-51/01-final-reseal-and-submission.md` not copied to reports/ |

## ACTIVE.md Links — Need Fix

ACTIVE.md rows 37-39 reference incorrect paths:
- Wave 49: `work/wave-49/01-transaction-atomicity.md` → should be `work/reports/wave-49/01-transaction-atomicity.report.md`
- Wave 50: `work/wave-50/01-deferred-security-risks.md` → should be `work/reports/wave-50/02-deterministic-test-suite.report.md`
- Wave 51: `work/wave-51/01-final-reseal-and-submission.md` → should be `work/reports/wave-51/01-final-reseal-and-submission.report.md` (directory missing)

## fresh_session_factory — NOT FOUND

```bash
git log --oneline --all -S "fresh_session_factory"
```
→ No commits contain this string. **NOT LANDED**.

## Summary for README / SUBMISSION

- Backend coverage: **45%**
- Frontend function coverage: **60.35%** (threshold: 60% — **MET**)
- TypeScript: **FAILING** (8 errors)
- ESLint: **FAILING** (3 errors)
- All Python gates: **PASSING**
- Alembic: **Single head (0036)**
- fresh_session_factory: **NOT FOUND**

**Verdict:** Frontend functions ABOVE threshold (60.35% > 60%), but TypeScript/ESLint have errors that should be cleaned before claiming thresholds met.