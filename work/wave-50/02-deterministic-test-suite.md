# Wave-50 Task 02 — Make the suite deterministic: no failures on a machine without Redis

## Why this matters more than it looks

Right now, **an evaluator who clones this repo and runs `pytest` sees 2 failures.** Verified this session, real output:

```
FAILED tests/wave-1/test_skeleton.py::test_readyz_db_ok - assert 503 == 200
FAILED tests/wave-36/test_observability.py::TestHealthEndpoints::test_readyz_returns_healthy_when_all_up
====== 2 failed, 564 passed, 7 skipped, 41 warnings in 2181.10s (0:36:21) ======
```

Both are **environmental, not defects** — `/readyz` correctly reports 503 when Redis is down, and Redis isn't running outside Docker. That's the endpoint working as designed. But a reader can't tell that from the output, and "the two failures are fine, trust us" is exactly the kind of claim this project's `HALL_OF_SHAME.md` exists to prevent.

Confirmed there is currently **no skip guard**: `grep -rn "skipif\|REDIS_URL" tests/wave-1/test_skeleton.py tests/wave-36/test_observability.py` → **0 hits**.

## Files you own
- `tests/wave-1/test_skeleton.py`
- `tests/wave-36/test_observability.py`
- `tests/conftest.py` (add one shared helper)
- `BACKLOG.md` (the "Environment-coupled tests" section)
- `README.md` (the backend-suite row, only if the number changes)

## The work

### 1. Add a real reachability check, not a guess
In `tests/conftest.py`, add a helper that **actually attempts a Redis connection** with a short timeout and caches the result for the session:

```python
@pytest.fixture(scope="session")
def redis_available() -> bool: ...
```

Do **not** decide based on the presence of an env var — `REDIS_URL` being set proves nothing about whether the server is up. Attempt the connection, catch the connection error, return a bool.

### 2. Skip (don't fake) the two Redis-coupled assertions
Mark both tests to skip when Redis is unreachable, with a **specific reason string** that says why — e.g. `"requires a running Redis; /readyz reports 503 without it (environmental, not a defect)"`. The reason shows up in pytest output and is the whole point: it converts a confusing red into a self-explaining skip.

**Do not** weaken the assertions to make them pass (e.g. accepting 503 as OK). The test asserting `/readyz == 200` when everything is up is a genuinely valuable test — it must still run and still pass in the Docker/CI path where Redis *is* up.

### 3. Confirm CI still exercises them for real
Find the workflow in `.github/workflows/` that brings up services. Verify Redis is among them, so these two tests **actually run and pass in CI** rather than silently skipping everywhere. If CI does not currently start Redis, add it. A test that skips in every environment is worse than one that fails honestly — say so in your report if you find that.

### 4. Reconcile the docs
- `BACKLOG.md`: the "Environment-coupled tests (parked until CI provides the service)" section — this task takes **option (a)** from the two it lists. Mark it resolved, name the commit.
- `README.md` / `HANDOFF.md`: if the local-run number changes (e.g. `564 passed / 2 failed / 7 skipped` → `564 passed / 0 failed / 9 skipped`), update it — **only with output you actually produced**, and say which environment produced it. The Docker-stack number (572/1/0) is a separate row and should not be blended with the local one.

## Acceptance criteria
- [ ] With Redis **down**: full backend suite runs with **0 failures**; the 2 tests report as skipped with a readable reason. Paste the real tail of the output.
- [ ] With Redis **up** (`docker compose up -d postgres redis`): the same 2 tests **run and pass** — not skipped. Paste that output too. **Both runs are required** — one alone doesn't prove the guard works.
- [ ] The CI workflow starts Redis, so these tests execute for real in CI (show the workflow lines)
- [ ] No assertion was weakened — diff shows skip markers added, not expectations lowered

## Deliver
`work/reports/wave-50/02-deterministic-test-suite.report.md`. Commit before writing it.

## Constraints
- Time budget: 90 min · commit per numbered item
- Two runs (Redis down, Redis up) are both mandatory evidence — a single run cannot demonstrate a conditional skip works
- If you cannot get Redis up locally to do the second run, **say so explicitly and mark that criterion NOT MEASURED**. Do not infer it. This project has a documented history of invented numbers (`HALL_OF_SHAME.md`) — an honest "not measured" is always accepted, a fabricated pass is not
