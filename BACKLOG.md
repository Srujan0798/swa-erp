# BACKLOG

> Wave-40 Task 01. Genuinely **parked** items pulled from this repo's own reports —
> not invented busywork. Each carries why it is parked and the guard that now keeps it
> honest. Items here are NOT claimed as done anywhere.

## Environment-coupled tests (parked until CI provides the service)
- **`tests/wave-1/test_skeleton.py::test_readyz_db_ok`** — asserts `/readyz` returns 200,
  but the test DB reports `503` when Redis is not running (readyz checks Redis liveness).
  Fails on any machine without Redis (this session: Redis unavailable → 503).
- **`tests/wave-36/test_observability.py::test_readyz_returns_healthy_when_all_up`** — same
  Redis coupling.
- **Status:** PARKED. Root cause is environmental, not a code bug. Two options:
  (a) mark these tests `skipif REDIS_URL unreachable`, or (b) run them only in the
  `docker-compose` CI job that brings Redis up. Until then they are an *environmental
  failure*, recorded in `results/metrics.json` → `environmental_failures`, never folded
  into the "real failure" count.
- **Guard:** `generate_metrics.sh` lists Redis-dependent failures under
  `environmental_failures` so they are not double-counted as product regressions.

## Wave-37 deferred RISKs (from `work/reports/wave-37/`)
These were found by adversarial review, fixed at the critical class, and **deliberately
deferred** as documented RISK — not hidden. Listed here so they are tracked, not lost.

| ID | Finding | Why parked | Class |
|----|---------|-----------|-------|
| SF-3 | GST default 18% schema default | India GST default intentional; documented | RISK |
| SF-4 / SEC-02 | `/metrics` endpoint unauthenticated | VPN/internal deploy; document in SUBMISSION | CONFIRMED RISK |
| SF-6/7 | Import rollback counter / savepoint | needs careful TDD; larger behavioral change | RISK / BUG |
| SF-8/9 | Broad `except` masking (rfqs.py, auth_service.py) | deferred; observability gap | RISK |
| SEC-04/05 | Time/finance read RBAC | product may want VIEWER reads; needs Viraj product call | RISK |
| SEC-06 | JWT logout / refresh rotation | deferred | RISK |
| SEC-07/08 | Job IDOR / document write roles | deferred | RISK |
| #7 import | Per-row `except` with no savepoint/rollback | needs repro with mid-import IntegrityError | MED RISK |
| #10 | `update_db_pool_metrics` bare `except: pass` (dead/unused) | dormant; dangerous if wired later | MED RISK |

- **Guard:** these are recorded as RISK in the wave-37 report; a future wave should
  close them with TDD. They must NOT be re-classified as "fixed" without a test.

- **Async export (Celery) is fully built but never triggered from the UI** — retries
  (max_retries=2), failure tracking, and a real `GET /api/jobs/{id}` status endpoint
  all work correctly, but zero frontend hooks or components reference `/api/jobs` or
  `async=true`. Not a live bug (nothing currently reaches the failure path from a real
  user action), but a dormant integration — either wire it up for large exports or
  document it as backend-only capability for future use.

- **DB index coverage checked, no gap found** — spot-checked `tasks.assignee_id`
  (composite index with status), `invoices.project_id`, `time_entries.{project_id,task_id,user_id}`,
  and `document_references.{project_id,token_id}` — all properly indexed. This item
  can be considered closed; re-check only if a new frequently-filtered column is
  added without an index.

## Larger structural debt (parked, out of this wave's scope)
- **Vitest coverage suppression on failure** — fixed mechanically by
  `generate_metrics.sh` (records `null` + reason), but the upstream vitest behaviour
  remains; a future wave could pin a vitest version or add a post-fail coverage pass.
- **FM-08 scope-guard padding** (see HALL_OF_SHAME #5) — mitigated; full HIERARCHY
  de-padding is a separate cleanup wave.

---
*Backlog entries are intentionally conservative. Nothing here is marked DONE. The truth
infrastructure (results/metrics.json + validators) exists so that any future "DONE"
claim is mechanically checkable.*
