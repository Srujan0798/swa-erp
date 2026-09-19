# Wave-49 Task 01 — Transaction atomicity (commit `f26b420`) — Verification Report

- HEAD at verification: `8652036` (`feat(security): METRICS_REQUIRE_AUTH flag, default True`)
- Verified commit: `f26b420de3ed0400ad4dd10233ba4152c1e217c3` — `fix(wave-49): atomic transaction wrapper for inquiry conversion path` (Tue Sep 15 2026)
- Working tree at verification: DIRTY (other agents' uncommitted changes, including `M src/backend/services/inquiry_service.py` — directly on the conversion path under test; see §5).
- Worker scope: report-only, no code changes made.

## 1. What `f26b420` claimed

```
- get_db() now commits once per request, rolls back on exception
- Convert mid-request commits to flushes in Inquiry→Client→Project path
- Add atomicity test proving orphan client is rolled back on project failure
- Remaining 18+ repos with mid-request commits backlogged (not fixed)
```

Files changed by `f26b420` (`git show --stat f26b420`): `audit_repo.py`, `client_repo.py`, `inquiry_repo.py`, `project_repo.py` (each 1 line: `db.commit()` → `db.flush()`), plus `get_db` session change and `tests/wave-49/test_inquiry_conversion_atomicity.py`.

## 2. Verification A — no mid-request `.commit()` in the two repos: PASS

Command: `grep -rn "\.commit()" src/backend/db/repositories/client_repo.py src/backend/db/repositories/project_repo.py`
RAW output: (empty) → `grep_exit=1` (no matches). The `commit()` → `flush()` conversion from `f26b420` is intact at HEAD:
```diff
-    db.commit()
+    db.flush()
```
in both `client_repo.py::create` and `project_repo.py::create_project` (confirmed via `git show f26b420 -- <both files>`).

## 3. Verification B — test run: 3 FAILED at HEAD (raw, not green)

Pre-check: `ps aux | grep pytest` → no competing run. Command: `python3 -m pytest tests/wave-49/ tests/wave-9/test_inquiries.py -v`
RAW summary:
```
FAILED tests/wave-49/test_inquiry_conversion_atomicity.py::test_convert_inquiry_rolls_back_client_on_project_failure - Failed: DID NOT RAISE <class 'RuntimeError'>
FAILED tests/wave-9/test_inquiries.py::TestConvertInquiryNewClient::test_no_existing_client_creates_client_and_project - AssertionError: assert None == 'Manufacturing'
 +  where None = <src.backend.models.client.Client object at 0x115081e00>.industry
FAILED tests/wave-9/test_inquiries.py::TestConvertInquiryNewClient::test_client_code_uses_reference_id_format - AssertionError: assert 'NEWCO-1' == 'SWA-2026-CLT-001'

  - SWA-2026-CLT-001
  + NEWCO-1
============= 3 failed, 15 passed, 5 warnings in 291.56s (0:04:51) =============
```
Re-run of exactly the 3 failing tests reproduced all 3 (`3 failed ... in 293.30s`), so this is deterministic at HEAD, not flaky. Detail on the atomicity test (`DID NOT RAISE RuntimeError` at `test_inquiry_conversion_atomicity.py:56`): the test monkeypatches project creation to raise, but logs show conversion succeeding (`inquiry.convert.project_created project_code=SWA-PRJ-001`), i.e. the failure-injection seam no longer fires.

## 4. Before/after

- Before `f26b420`: `client_repo.create` / `project_repo.create_project` called `db.commit()` mid-request → a project-creation failure after client insert left an orphan client row (the defect).
- After `f26b420` (still true at HEAD per grep): both use `db.flush()`; commit happens once per request in `get_db()`, rollback on exception.

## 5. DoD checklist

- [x] `grep .commit()` in `client_repo.py` + `project_repo.py` is empty — PASS (code-level claim of `f26b420` holds at HEAD)
- [ ] `tests/wave-49/ tests/wave-9/test_inquiries.py` green — FAIL: 3 failed / 15 passed (raw above; fabricated green NEVER)
- [ ] Atomicity behavior proven by test — NOT PROVEN at HEAD: the rollback test itself errors (`DID NOT RAISE`), so no behavioral evidence either way

## 6. Residual risks / likely causes (for owning agent, not fixed here)

1. The 2 `wave-9` failures look like **later-commit drift**, not an `f26b420` regression: `reference_id_service.py` was rewritten in `fda369e` (client code now `NEWCO-1` instead of `SWA-2026-CLT-001`) and industry mapping no longer populates from inquiry. The tests assert the old contract.
2. The atomicity-test failure (`DID NOT RAISE`) is consistent with the uncommitted `M src/backend/services/inquiry_service.py` in the dirty tree and/or the `788304d` logging refactor changing the conversion seam the test patches. Re-verify on a clean tree before blaming `f26b420`.
3. `f26b420` itself discloses 18+ other repos still commit mid-request — atomicity covers only the Inquiry→Client→Project path.
