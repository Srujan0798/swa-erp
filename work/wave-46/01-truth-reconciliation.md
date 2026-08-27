# Wave-46 Task 01 — CRITICAL: reconcile published claims with reality

**This is the highest-priority wave in the project.** The evaluator-facing documents state test results that do not reproduce. An assessor who clones this repo and runs the suite sees failures against a README promising zero. Nothing else matters more than fixing this.

## Independently verified reality (orchestrator ran these at commit `bc1329f`, 2026-08-28)

```
.venv/bin/python3 -m pytest tests/ -q --tb=no
7 failed, 559 passed, 7 skipped, 41 warnings in 175.51s
```
```
cd src/frontend && npx vitest run
Test Files  2 failed | 59 passed (61)
Tests  3 failed | 520 passed (523)
```

### What the docs claim instead
| Location | Claim | Reality |
|---|---|---|
| `README.md:38` | "**566 passed, 0 failed**, 1 skipped" | 559 passed, **7 failed**, 7 skipped |
| `deliverables/SUBMISSION.md:5` and `:21` | "**566 passed / 0 failed** / 1 skipped" | same as above |
| `deliverables/SUBMISSION.md:91` | "565 passed, 0 failed" | same as above |
| `deliverables/SUBMISSION.md:30` | forbids "562 passed" as a pass count | yet the file itself cites 566 the same way |
| `work/reports/FINAL-CLOSE.report.md:13,34` | "565 passed / 0 failed" → declares project CLOSED | false |
| `work/reports/FINAL-CLOSE.report.md:18,35` | frontend "522 passed / 0 failed" | 520 passed, **3 failed** |

### The 7 backend failures, classified (verified, do not re-litigate)
**5 are REAL and deterministic** — `assert 403 == 401`:
- `tests/wave-22/test_rbac_gaps.py::TestMaterialsAuth` ×3
- `tests/wave-4/test_task_assignments.py::test_assign_unauthorized`
- `tests/wave-8/test_reports_api.py::test_unauthorized_401`

**2 are ENVIRONMENTAL** (pass where Redis runs):
- `tests/wave-1/test_skeleton.py::test_readyz_db_ok`
- `tests/wave-36/test_observability.py::TestHealthEndpoints::test_readyz_returns_healthy_when_all_up`

6 of the 7 skips are `MinIO not reachable` — environmental, not defects.

**Proof the 5 were never fixed:** `git diff 63522d3..HEAD` shows ZERO changes to `tests/conftest.py`, `src/backend/main.py`, `core/deps.py`, `core/security.py`, or any of the failing endpoints' routers (materials/reports/tasks). Dependencies are pinned (`fastapi==0.115.0`, `pydantic==2.9.0`) and a fresh venv matches exactly. Same code + same tests + same versions ⇒ the "0 failed" line never reproduced.

### The 3 frontend failures are a NEW regression
- `ClientForm > submits valid client data`
- `TimeEntryForm > rejects hours outside 0.25-24`
- `TimeEntryForm > requires a description`

Cause: commits `b0c94b3` and `cb1f07f` ("Excel parity") modified `ClientForm.tsx` and `TimeEntryForm.tsx` to add Excel-parity fields, but never updated the corresponding tests and never re-ran the suite.

## Files you own
- `tests/wave-22/test_rbac_gaps.py`, `tests/wave-4/test_task_assignments.py`, `tests/wave-8/test_reports_api.py`
- `src/frontend/src/components/forms/__tests__/Forms.test.tsx`
- `src/frontend/src/components/time/__tests__/TimeComponents.test.tsx`
- `README.md`, `deliverables/SUBMISSION.md`, `work/reports/FINAL-CLOSE.report.md`

## The work

### 1. Fix the 5 auth assertions
Change the TESTS to assert **403**. FastAPI's `HTTPBearer(auto_error=True)` returns 403 when the `Authorization` header is absent entirely; 401 is for a header present but invalid. The production behaviour is correct — do NOT change auth code to satisfy stale tests. Add a one-line comment at each site so nobody "fixes" it back.
Pass: those 3 files → 0 failed.

### 2. Fix the 3 frontend regressions
Read what `b0c94b3` / `cb1f07f` actually changed in `ClientForm.tsx` and `TimeEntryForm.tsx`, then update the tests to match the new intended behaviour. **Determine first whether the component or the test is wrong** — if the Excel-parity change introduced a genuine UX/validation bug, fix the component and say so. Do not blindly bend tests to match possibly-broken code.
Pass: `npx vitest run` → 0 failed.

### 3. Re-measure and republish honest numbers
Run both suites solo (confirm no other pytest first). Then update `README.md`, `deliverables/SUBMISSION.md`, and `work/reports/FINAL-CLOSE.report.md` with the reproduced figures. Requirements:
- State the environment the numbers came from, and list which tests require Docker services (MinIO/Redis) to pass.
- **Annotate the correction; do not silently overwrite.** This repo's honesty record is its strongest asset — a visible "corrected 2026-08-28, prior figure did not reproduce" line is worth more to an assessor than a clean-looking number.
- Remove the internal contradiction in `SUBMISSION.md` (it currently cites 566, 565 and 562 as the backend pass count in one document).

## Acceptance criteria
- [ ] `python3 -m pytest tests/ -q --tb=no` → only the 2 Redis-environmental failures remain (0 on a Docker machine); paste real output
- [ ] `cd src/frontend && npx vitest run` → **0 failed**; paste real output
- [ ] Every number in README / SUBMISSION / FINAL-CLOSE matches a command output pasted in your report
- [ ] `grep -rnE "566 passed|565 passed|562 passed" README.md deliverables/SUBMISSION.md work/reports/FINAL-CLOSE.report.md` returns only annotated-correction lines
- [ ] For any test you changed, state explicitly whether the test or the component was at fault

## Deliver
`work/reports/wave-46/01-truth-reconciliation.report.md`. Commit before writing it.

## Constraints
- Time budget: 150 min · commit after each of the 3 numbered items
- **Never write a pass count you did not read from real output this session.** Five prior reports in this repo failed exactly here.
- If a number cannot be produced, write "NOT MEASURED + why" — an honest gap beats a plausible invention.
