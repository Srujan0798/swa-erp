# Wave-46 Task 01 — CRITICAL: reconcile published claims with reality

**Status:** DONE with honest gaps recorded. Frontend suite green. Backend suite count marked unmeasured in this session because Postgres was unavailable; the 5 auth test fixes are real and were verified when Postgres was available. Frontend metrics republished with visible correction annotation. Auth-test source-of-truth identified: tests were stale, FastAPI auth behavior is correct.

## 1. Fix the 5 auth assertions

Changed the tests to assert **403** for missing `Authorization` headers.

Files modified:
- `tests/wave-22/test_rbac_gaps.py`
- `tests/wave-4/test_task_assignments.py`
- `tests/wave-8/test_reports_api.py`

Fault: **tests were wrong**. Production auth behavior is correct — `HTTPBearer(auto_error=True)` returns 403 when the `Authorization` header is absent entirely. 401 is reserved for a present-but-invalid credential. Added one-line comments at each site so nobody “fixes” it back.

Commit: `657a961` wave-46: align auth tests with FastAPI HTTPBearer behavior (403 for missing auth)

Verification:
- Targeted run passed:
  - `tests/wave-22/test_rbac_gaps.py::TestMaterialsAuth` x3 → **passed**
  - `tests/wave-4/test_task_assignments.py::test_assign_unauthorized` → **passed**
  - `tests/wave-8/test_reports_api.py::test_unauthorized_401` → **passed**
- Full suite could not be reproduced in this session because Postgres became unavailable mid-run (`server closed the connection unexpectedly`). The targeted run proves the 5 assertions are fixed.

## 2. Fix the 3 frontend regressions

Commits `b0c94b3` and `cb1f07f` changed `ClientForm.tsx` and `TimeEntryForm.tsx` to add Excel-parity fields and rename labels, but never updated the corresponding tests.

Files modified:
- `src/frontend/src/components/forms/__tests__/Forms.test.tsx`
- `src/frontend/src/components/time/__tests__/TimeComponents.test.tsx`

Fault: **tests were wrong**. The components intended:
- `primary_email` label changed to `Email *`
- `TimeEntryForm` hours label changed to `Hours logged *`
- `TimeEntryForm` description error changed to `Description / remarks is required`

Updated tests to match the new intended behavior.

Commit: `ab73a2b` wave-46: update frontend tests to match post-excel-parity ClientForm/TimeEntryForm behavior

Verification:
```
cd src/frontend && npx vitest run
Test Files  61 passed (61)
Tests  523 passed (523)
```

## 3. Re-measure and republish honest numbers

Updated evaluator-facing docs with the reproduced figures and visible correction annotations.

Files modified:
- `README.md`
- `deliverables/SUBMISSION.md`
- `work/reports/FINAL-CLOSE.report.md`

Changes:
- Backend suite count marked **NOT MEASURED** in this session because Postgres was unavailable (`server closed the connection unexpectedly`). Added a visible correction note instructing future runners to reproduce on a machine with Docker/Postgres/Redis/MinIO.
- Frontend suite count updated from stale `522 passed / 0 failed` to verified `523 passed / 0 failed` from this session.
- `SUBMISSION.md` internal contradiction resolved: removed the stale `566 passed / 0 failed / 1 skipped` claim from the status line and metrics table, replaced with NOT MEASURED + correction annotation.
- Frontend failures are fixed in code; the regressions were test-side, not component-side.

Commit: `ab7e504` wave-46: annotate corrected metrics; mark unverified backend suite count

## Important caveat

The free worker model `opencode/mimo-v2.5-free` returned `Rate limit exceeded` on the initial run, and a subsequent retry returned `Unexpected server error`. This wave was executed directly by the orchestrator instead. All code/test changes and commits are real; the report is being written from actual command output where available.

## Acceptance criteria

- [x] 5 auth tests changed to assert **403**; targeted pytest run passed all 5
- [ ] `python3 -m pytest tests/ -q --tb=no` → only 2 Redis-environmental failures remain (0 on a Docker machine) — **BLOCKED**: Postgres unavailable in this session; rerun on a machine with Docker/Postgres/Redis/MinIO
- [x] `cd src/frontend && npx vitest run` → **523 passed / 0 failed**
- [x] Numbers in README / SUBMISSION / FINAL-CLOSE now match actual command outputs, with visible correction annotations
- [x] `grep -rnE "566 passed|565 passed|562 passed|522 passed" README.md deliverables/SUBMISSION.md work/reports/FINAL-CLOSE.report.md` now returns only annotated-correction lines or no matches
- [x] For every changed test, the report states the test was at fault, not the component

## Commits

1. `657a961` wave-46: align auth tests with FastAPI HTTPBearer behavior (403 for missing auth)
2. `ab73a2b` wave-46: update frontend tests to match post-excel-parity ClientForm/TimeEntryForm behavior
3. `ab7e504` wave-46: annotate corrected metrics; mark unverified backend suite count
