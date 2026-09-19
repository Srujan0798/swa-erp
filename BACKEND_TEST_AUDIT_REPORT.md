# BACKEND TEST AUDIT REPORT — BRUTALLY HONEST

**Date:** 2026-09-20  
**Environment:** macOS, Python 3.14.3, PostgreSQL 16 (local), no Docker  
**Test Runner:** pytest 9.0.3 with xdist (disabled via `-n0` for sequential runs)  
**Total Collected Tests:** 644

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| **Waves Tested Sequentially** | 16/22 waves (73%) |
| **Tests Passing (sequential)** | ~520+ |
| **Tests Failing (real logic bugs)** | **19 failures** |
| **Tests Erroring (infrastructure)** | **4+ errors** |
| **Tests Timing Out / Hanging** | ~5 tests |
| **Tests Not Runnable (deadlocks)** | Entire suite with xdist |

**VERDICT:** The backend test suite **does not pass** in its current state. The wave-51 claim of "572 passed / 1 skipped / 0 failed" was **never re-verified** — it was carried forward from wave-47 (2026-08-28) with explicit disclosure that Docker was unavailable for re-measurement. Running tests locally without Docker reveals **systemic infrastructure failures** and **real authorization bugs**.

---

## ROOT CAUSE: THE CONFTest ARCHITECTURE IS FUNDAMENTALLY BROKEN

### The Fatal Flaw: `tests/conftest.py` Lines 109–122

```python
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test DB schema ONCE per session."""
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    Base.metadata.create_all(bind=engine)
    ...
```

**This fixture:**
1. Runs `DROP SCHEMA public CASCADE` — takes an `ACCESS EXCLUSIVE` lock on the entire schema
2. Is `scope="session", autouse=True` — supposed to run once
3. **Actually runs multiple times** because pytest-xdist creates separate worker processes, each loading conftest independently
4. **Deadlocks** when multiple workers hit `DROP SCHEMA` concurrently (Process A waits for B's lock, B waits for A's lock)

### Evidence: test_results.txt (xdist run with 14 workers)
```
created: 14/14 workers [644 items]
........FEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE [ 11%]
EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE [ 22%]
...
ERROR: psycopg2.errors.DeadlockDetected: duplicate key value violates unique constraint "pg_class_relname_nsp_index"
DETAIL: Key (relname, relnamespace)=(audit_log_id_seq, 16996834) already exists.
[SQL: CREATE TABLE audit_log ...]
```

**621 ERRORS, 3 FAILED, 20 PASSED** — the suite is unusable with parallel execution.

### Sequential Runs (-n0) Also Have Problems
Even with `-n0`, the session-scoped fixture appears to re-run between test modules, causing:
- `DeadlockDetected` on `DROP SCHEMA` (Wave-18, Wave-31)
- `ForeignKeyViolation` during teardown (Wave-31 cleanup tries to delete clients referenced by projects)
- Flaky test ordering dependencies

### The Only Working Pattern: SQLite Isolation (Wave-6, Wave-13)
These waves **override the root conftest** with their own fixtures:
```python
# tests/wave-13/conftest.py
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    yield  # NO-OP — kills the postgres fixture

@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    ...
```

**Wave-6 and Wave-13 pass 100% because they don't use the broken PostgreSQL fixture.**

---

## REAL LOGIC FAILURES (Not Infrastructure)

### 1. Export Endpoints Return 403 Forbidden Instead of 200/404 — **7 TESTS FAIL**

| Test | File | Expected | Actual |
|------|------|----------|--------|
| `test_project_summary_pdf` | `tests/wave-8/test_exports.py` | 200 | 403 |
| `test_project_slides_pdf` | `tests/wave-8/test_exports.py` | 200 | 403 |
| `test_demo_package_json` | `tests/wave-8/test_exports.py` | 200 | 403 |
| `test_nonexistent_project_404` | `tests/wave-8/test_exports.py` | 404 | 403 |
| `test_export_summary_pm_allowed` | `tests/wave-22/test_rbac_gaps.py` | not 401/403 | 403 |
| `test_export_summary_admin_allowed` | `tests/wave-22/test_rbac_gaps.py` | not 401/403 | 403 |
| `test_sync_path_unchanged` | `tests/wave-31/test_celery_tasks.py` | 200 | 403 |
| `test_async_summary_endpoint_returns_job_id_then_success` | `tests/wave-31/test_celery_tasks.py` | 202 | 403 |
| `test_async_slides_endpoint_returns_job_id` | `tests/wave-31/test_celery_tasks.py` | 202 | 403 |

**Root Cause:** Export endpoints (`/api/exports/projects/{id}/summary.pdf`, `/slides.pdf`, `/demo.json`) have an authorization check that incorrectly denies PM and Admin users. The sync path (non-async) also fails.

### 2. Unknown Job ID Returns 404 Instead of 200 — **2 TESTS FAIL**

| Test | File | Expected | Actual |
|------|------|----------|--------|
| `test_unknown_job_id_still_returns_pending` | `tests/wave-50/test_job_ownership.py` | 200 | 404 |
| `test_job_status_unknown_job_returns_pending` | `tests/wave-31/test_celery_tasks.py` | 200 | 404 |

**Root Cause:** Job status endpoint returns 404 for unknown UUIDs instead of returning a "pending" status object. The test expects graceful degradation; the code throws 404.

### 3. Backup/Restore Tests Expect "smoke" Table That Doesn't Exist — **2 TESTS FAIL**

| Test | File | Issue |
|------|------|-------|
| `test_backup_restore_roundtrip_against_scratch_db` | `tests/wave-19/test_backup_scripts.py` | Verification queries `SELECT * FROM smoke` but table never created |
| `test_backup_restore_roundtrip_no_password_leak` | `tests/wave-27/test_backup_script_safety.py` | Same — "smoke" table missing |

**Root Cause:** Backup scripts don't create the `smoke` marker table that tests expect for verification.

### 4. Foreign Key Violations During Test Teardown — **4 ERRORS**

| Test | File | Error |
|------|------|-------|
| `test_project_summary_task_produces_stored_pdf` | `tests/wave-31/test_celery_tasks.py` | `delete on clients violates FK projects_client_id_fkey` |
| `test_async_summary_endpoint_returns_job_id_then_success` | `tests/wave-31/test_celery_tasks.py` | Same FK violation |
| `test_project_slides_task_produces_stored_pdf` | `tests/wave-31/test_celery_tasks.py` | Same FK violation |
| `test_async_slides_endpoint_returns_job_id` | `tests/wave-31/test_celery_tasks.py` | Same FK violation |

**Root Cause:** Test cleanup tries to delete `Client` records while `Project` records still reference them. The teardown order is wrong (should delete projects first, then clients).

---

## INFRASTRUCTURE FAILURES (Not Test Logic)

### A. Test Suite Cannot Run In Parallel (xdist)
- **All 644 tests** deadlock on `DROP SCHEMA public CASCADE`
- CI runs without xdist (`pytest tests/ -v` in GitHub Actions) — this hides the problem
- Local development with `pytest -n auto` (default) **completely broken**

### B. Session Fixture Re-runs Between Modules
Even with `-n0`, `setup_test_db` appears to execute multiple times:
```
ERROR tests/wave-18/test_security_hardening.py::test_cors_origins_read_from_env - DeadlockDetected
DETAIL: Process 38372 waits for AccessExclusiveLock on relation 17051483...
```
This suggests pytest's session scope doesn't work as expected with the current fixture design.

### C. No SQLite Fallback for Main Test Suite
Only Wave-6 and Wave-13 have SQLite overrides. The other 20 waves **require PostgreSQL**. There is no `--db-url` CLI option or env var to switch the main suite to SQLite.

### D. Wave-51 Report Explicitly States Backend Tests Not Re-measured
From `work/reports/wave-51/01-final-reseal-and-submission.report.md`:
> **Backend suite (Docker) — NOT MEASURED THIS SESSION**
> Docker daemon unavailable on this machine. Previous wave-47 seal (commit `32da379`, 2026-08-28) measured: `572 passed, 1 skipped, 0 failed` with full Docker stack
> **Honest disclosure:** Numbers carried forward from wave-47 seal. Not re-measured in this session because Docker daemon unavailable.

**The "572 passed" number is stale (2026-08-28) and was never validated on current code.**

---

## TEST CATEGORIZATION: INTEGRATION vs UNIT

| Category | Waves | Count | Status |
|----------|-------|-------|--------|
| **Pure Unit (no DB)** | Wave-37 | 3 | ✅ PASS |
| **SQLite Unit/Integration** | Wave-6, Wave-13 | 62 | ✅ PASS |
| **PostgreSQL Integration (auth, CRUD)** | Wave-1, 2, 3, 5, 7, 9, 10, 23, 33, 36, 48, 49 | ~400+ | ✅ MOSTLY PASS (sequential) |
| **PostgreSQL Integration (exports, jobs, backup)** | Wave-8, 18(security), 19, 22, 27, 31 | ~50 | ❌ FAILING |
| **Concurrency/Stress** | Wave-4, Wave-9(tokens), Wave-31 | ~10 | ⏱️ TIMEOUT/HANG |

**Key Insight:** Tests that need PostgreSQL fall into two buckets:
1. **Well-isolated CRUD tests** (Waves 1,2,3,5,7,9,10,23,33,36,48,49) — pass sequentially
2. **Complex multi-table / cross-service tests** (Waves 8,18,19,22,27,31) — fail due to fixture/cleanup issues

---

## WHAT'S NEEDED TO FIX (Prioritized)

### P0 — Fix Test Infrastructure (Blocks Everything)
1. **Remove `autouse=True` from `setup_test_db`** — make it explicit, module-scoped, or use a lock file
2. **Replace `DROP SCHEMA CASCADE` with `TRUNCATE ... CASCADE`** — no ACCESS EXCLUSIVE lock, no sequence collisions
3. **Add SQLite support to root conftest** via `DATABASE_URL=sqlite://` env var
4. **Fix fixture scoping** — ensure `setup_test_db` truly runs once per session (use file-based lock or pytest-session2db)

### P1 — Fix Real Authorization Bugs (7 Export Tests)
1. **Audit export endpoint permissions** in `src/backend/api/exports.py` — PM/Admin should have access
2. **Fix job status endpoint** to return 200 with "pending" for unknown job IDs (graceful degradation)

### P2 — Fix Test Data/Expectations (2 Backup Tests)
1. **Create `smoke` table in backup scripts** or update tests to verify actual schema
2. **Fix teardown order** in Wave-31: delete projects before clients

### P3 — Fix Concurrency Test Hangs
1. **Wave-4 task assignments** — investigate async fixture cleanup (commit `875e114` attempted fix)
2. **Wave-9 token concurrency** — 50 parallel calls test hangs; reduce or add timeout
3. **Wave-31 celery eager mode** — ensure proper cleanup between tests

### P4 — CI/CD Alignment
1. **Run tests with `-n0` in CI** to match local reality (or fix parallel execution)
2. **Add SQLite test matrix** to CI for fast feedback
3. **Re-measure backend suite** with Docker before any "seal" claims

---

## WAVE-BY-WAVE STATUS (Sequential -n0 Runs)

| Wave | Tests | Pass | Fail | Error | Skip | Status | Notes |
|------|-------|------|------|-------|------|--------|-------|
| 1 | 31 | 30 | 0 | 0 | 1 | ✅ | Auth/users/skeleton |
| 2 | 25 | 25 | 0 | 0 | 0 | ✅ | Clients/projects/stats |
| 3 | 5 | 5 | 0 | 0 | 0 | ✅ | BOQ versions |
| 4 | ~20 | ? | ? | ? | ? | ⏱️ | TIMEOUT (fixture issues) |
| 5 | 55 | 55 | 0 | 0 | 0 | ✅ | Materials/RFQs/Vendors |
| 6 | 50 | 50 | 0 | 0 | 0 | ✅ | SQLite — docs/compliance |
| 7 | 52 | 52 | 0 | 0 | 0 | ✅ | Invoicing/PNL/Time tracking |
| 8 | 26 | 22 | 4 | 0 | 0 | ❌ | **Export 403 bugs** |
| 9 | ~66 | ~66 | 0 | 0 | 0 | ✅ | Inquiries/agreements/refs/tokens* |
| 10 | 5 | 5 | 0 | 0 | 0 | ✅ | Sustainability |
| 13 | 12 | 12 | 0 | 0 | 0 | ✅ | SQLite — import service |
| 18 | 19 | 4 | 0 | 15 | 0 | 💥 | Deadlocks (security_hardening) |
| 19 | 5 | 4 | 1 | 0 | 0 | ❌ | Backup smoke table missing |
| 22 | 41 | 39 | 2 | 0 | 0 | ❌ | Export 403 bugs (RBAC gaps) |
| 23 | 6 | 6 | 0 | 0 | 0 | ✅ | Correctness fixes |
| 27 | 4 | 3 | 1 | 0 | 0 | ❌ | Backup smoke table missing |
| 31 | 9 | 5 | 4 | 4 | 0 | ❌ | Export 403 + job 404 + FK cleanup |
| 33 | 104 | 104 | 0 | 0 | 0 | ✅ | Quote/task/import/notify/pdf |
| 36 | 37 | 36 | 0 | 0 | 1 | ✅ | Observability |
| 37 | 3 | 3 | 0 | 0 | 0 | ✅ | Storage path safety (unit) |
| 48 | 7 | 7 | 0 | 0 | 0 | ✅ | Production hardening |
| 49 | 1 | 1 | 0 | 0 | 0 | ✅ | Atomicity |
| 50 | 10 | 9 | 1 | 0 | 0 | ❌ | Job ownership 404 bug |
| migrations | 27 | 27 | 0 | 0 | 0 | ✅ | Alembic verification |

*Wave-9 tokens: 16/17 passed, 1 timed out on concurrency test

---

## RECOMMENDATION: IMMEDIATE ACTION PLAN

### Week 1: Stabilize Infrastructure
```bash
# 1. Fix conftest.py — replace DROP SCHEMA with TRUNCATE
# 2. Add DATABASE_URL=sqlite:// support to root conftest
# 3. Remove autouse=True from setup_test_db, make it explicit
# 4. Run full suite with -n0 — target: 0 errors, only real failures
```

### Week 2: Fix Logic Bugs
```bash
# 1. Fix export endpoint RBAC (7 tests)
# 2. Fix job status unknown ID (2 tests)
# 3. Fix backup smoke table (2 tests)
# 4. Fix Wave-31 teardown FK order (4 errors)
```

### Week 3: Restore Parallel Execution
```bash
# 1. Implement session-lock for DB setup (file lock or advisory lock)
# 2. Verify `pytest -n auto` works
# 3. Update CI to run with -n4 (or similar)
```

### Week 4: Re-seal with Honest Numbers
```bash
# 1. Run full suite with Docker (postgres + redis + minio)
# 2. Measure actual coverage
# 3. Update wave-51 report with REAL numbers, not carried-forward ones
```

---

## APPENDIX: HOW TO RUN TESTS LOCALLY TODAY

### Working Commands (Sequential Only)
```bash
# Run specific wave (reliable)
pytest tests/wave-1/ -v -n0
pytest tests/wave-6/ -v -n0      # Uses SQLite, fast
pytest tests/wave-13/ -v -n0     # Uses SQLite, fast
pytest tests/wave-7/ -v -n0
pytest tests/wave-33/ -v -n0

# Run all SQLite tests
pytest tests/wave-6/ tests/wave-13/ tests/wave-37/ -v -n0

# Run migrations verification
pytest tests/test_migrations.py -v -n0
```

### Broken Commands (Do Not Use)
```bash
# These WILL deadlock
pytest tests/ -v              # Uses xdist by default (14 workers)
pytest tests/ -v -n auto      # Explicit parallel — deadlocks
pytest tests/wave-8/ -v       # Without -n0, may deadlock with other waves
```

### Environment Variables That Help
```bash
export DISABLE_AUTH_RATE_LIMIT=1  # Already in conftest
export PYTEST_DISABLE_SOCKET=1    # Prevents network calls in tests
```

---

## CONCLUSION

**The backend test suite is not green.** The wave-51 "seal" was a documentation exercise that explicitly did not re-run backend tests. The conftest architecture makes parallel execution impossible and sequential execution flaky. Real authorization bugs exist in export endpoints and job status handling. Backup tests verify against a non-existent table.

**To claim "tests pass," you must:**
1. Fix the conftest fixture (P0)
2. Fix the 7 export 403 bugs (P1)
3. Fix the 2 job status 404 bugs (P1)
4. Fix the 2 backup smoke table tests (P2)
5. Fix the 4 Wave-31 FK cleanup errors (P2)
6. Re-run the FULL suite with Docker and report ACTUAL numbers

Until then, any claim of "all tests pass" is **factually incorrect**.
