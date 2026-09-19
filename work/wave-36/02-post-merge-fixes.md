# Wave-36 Task 02 — Fix real post-merge regressions in observability

Wave-36 (observability) passed its own isolated test run, but when merged with wave-32 (CI/mypy
refactor) and wave-34 (frontend tests) on `main`, independent verification found **3 real
failures** that wave-36's own report did not catch. Fix them for real — this is exactly the kind
of "each wave passes alone, breaks combined" bug this project has hit before (see
`docs/PROJECT_HISTORY.md` if it exists, or `git log --oneline | grep remote_side` for a past
example).

## Verified failures (commit `30f68aa` on `main`)

```
python3 -m pytest tests/wave-1/test_skeleton.py::test_readyz_db_ok tests/wave-36/test_observability.py -q
```

### 1. `/metrics` returns 404
```
FAILED tests/wave-36/test_observability.py::TestMetricsEndpoint::test_metrics_endpoint_exists
FAILED tests/wave-36/test_observability.py::TestMetricsEndpoint::test_metrics_content_type
FAILED tests/wave-36/test_observability.py::TestMetricsEndpoint::test_metrics_contains_http_requests_total
FAILED tests/wave-36/test_observability.py::TestMetricsEndpoint::test_metrics_contains_request_duration
FAILED tests/wave-36/test_observability.py::TestMetricsEndpoint::test_metrics_contains_in_flight
```
`GET /metrics` returns `{"detail":"Not Found"}` (404) in the test client. Check
`src/backend/core/metrics.py` and how it's wired into `src/backend/main.py` — likely the router
is only mounted when an env var (`ENABLE_METRICS`?) is set, and the test fixture / `.env.test`
doesn't set it, or the router registration has a bug. Fix so the tests (which represent the real
acceptance criteria from `work/wave-36/01-observability.md`) pass without requiring special env
setup the test suite doesn't provide — or, if gating behind an env var is intentional, fix the
test fixtures to set it, whichever is the actually-intended design. Verify by re-running the
listed tests.

### 2. `/readyz` response shape regressed an existing test
```
FAILED tests/wave-1/test_skeleton.py::test_readyz_db_ok - KeyError: 'db'
```
`tests/wave-1/test_skeleton.py` (wave-1, predates wave-36) expects `response.json()["db"] ==
"ok"`. Wave-36's `/readyz` rewrite changed the response shape and broke this. Two options — pick
whichever matches wave-36's actual intended schema, do not just patch the assertion blindly:
- If wave-36's new shape is correct and richer (e.g. `{"checks": {"db": "ok", "redis": "ok"}}`),
  update `tests/wave-1/test_skeleton.py` to match the new shape.
- If the old flat `{"db": "ok"}` shape was actually the intended contract, fix `/readyz` in
  `src/backend/api/health.py` to preserve it while still doing the real DB/Redis/migration
  checks wave-36 added.
Check `docs/OBSERVABILITY.md` (written in wave-36) for what shape was documented — the fix should
match the documentation, or the documentation needs correcting too if it's wrong.

### 3. Sentry init test fails
```
FAILED tests/wave-36/test_observability.py::TestErrorTracking::test_init_sentry_with_dsn_returns_true
  assert False is True
```
`src/backend/core/errors.py` — with a DSN set, `init_sentry()` (or equivalent) should return/set
`_sentry_initialized = True`. Currently returns `False`. Debug why — likely something in the
Sentry SDK init call is raising/failing silently, or a `DeprecationWarning` from
`FastApiIntegration(failed_request_status_codes=...)` (visible in the test output — the SDK
now wants a `set` of ints, not a list/None) is actually breaking init in this SDK version. Fix
the init call to match the installed `sentry-sdk` version's actual API.

## Files likely to touch
- `src/backend/core/metrics.py`
- `src/backend/core/errors.py`
- `src/backend/api/health.py`
- `tests/wave-1/test_skeleton.py` (only if the readyz shape change is confirmed correct)
- `docs/OBSERVABILITY.md` (if the documented contract needs correcting)

## Do NOT touch
- Anything outside observability (metrics/errors/health) — this is a targeted regression fix,
  not a new feature wave.

## Acceptance criteria
- [ ] All 3 failure groups above pass — paste real pytest output for each
- [ ] `python3 -m pytest tests/ -q` full suite — paste output. Baseline to beat: 445 passed,
      1 skipped, 8 failed (5 pre-existing 401-vs-403 unrelated to this wave — do not touch those).
      After your fix: those 8 (or fewer, don't worsen) should be the only failures left.
- [ ] `docs/OBSERVABILITY.md` still accurately describes the real `/readyz` and `/metrics`
      behavior after your fix

## Deliver
Report → `work/reports/wave-36/02-post-merge-fixes.report.md` with real before/after pytest
output for each of the 3 issues. Commit before writing the report.

## Constraints
- Time budget: 90 min
- Commit after each of the 3 fixes independently verified, not all at once
- Allowed: file edit, git, pytest, curl
