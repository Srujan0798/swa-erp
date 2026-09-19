# Wave-36 Task 01 — Production observability (metrics + error tracking)

**Depends on wave-32.** Best run after 35 (load testing reveals what's worth instrumenting).

## The problem

`plan/ARCHITECTURE.md` originally claimed Sentry and Prometheus were "integrated." A 2026-07-21
audit found **neither existed** — the docs were corrected to mark them target-state, but the
capability was never built.

What exists today: structured logging via `structlog` (`src/backend/core/middleware.py`) with
`X-Request-ID` correlation. That's a genuine foundation — but there is no way to answer "is the
system healthy right now?" or "what broke for that user?" without reading raw logs.

For a system about to run a company's operations on-prem with **no IT department** (Viraj
confirmed), this matters more than usual: when something breaks, there is no ops team to
diagnose it. The system has to be able to say what's wrong.

## Files to modify/create
- `src/backend/core/metrics.py` — Prometheus metrics + `/metrics` endpoint
- `src/backend/core/errors.py` — error tracking integration (env-gated)
- `src/backend/main.py` — wire both
- `.env.example`, `.env.production.example`, `docker-compose.yml`
- `docs/OBSERVABILITY.md` — what's collected, how to read it, how to alert
- `tests/wave-36/test_observability.py`

## Files you must NOT touch
- The existing `structlog` middleware — extend it, don't replace working logging
- Business logic — instrumentation must not change behaviour

## The work

### 1. Metrics (`/metrics`, Prometheus format)
Use `prometheus-fastapi-instrumentator` or equivalent. Expose at minimum:
- Request count / duration / in-flight, by endpoint + status class
- DB connection pool utilisation
- Celery queue depth + task success/failure counts (wave-31 built the worker)
- Business counters worth alerting on: failed logins, 5xx rate

**Gate `/metrics` behind auth or bind it internally** — do not expose operational internals
unauthenticated, even on an internal network.

### 2. Error tracking
`SENTRY_DSN` already exists as an empty optional env var. Wire it properly:
- **Env-gated**: absent DSN → no-op, zero overhead, no crash. Must work fine unconfigured, since
  the client may never set it up.
- Capture unhandled exceptions with request context + the existing request ID
- **Scrub PII and secrets before sending** — this handles real client business data. Verify
  scrubbing works; don't assume the SDK defaults are sufficient.

### 3. Health endpoints — make them real
`/healthz` currently returns `{"status":"ok"}` unconditionally — it's a liveness probe that can't
detect anything. Add a genuine **readiness** check: DB reachable, Redis reachable, migrations at
head. Keep `/healthz` as cheap liveness; put the real checks in `/readyz`.

### 4. The honest bit
If any piece can't be completed in budget, **do not update the docs to claim it exists.** This
repo has a documented history of exactly that failure (the Sentry/Prometheus claims this wave is
fixing). Ship what's real, mark the rest target-state.

## Acceptance criteria
- [ ] `/metrics` returns valid Prometheus output; scraping it shows request counts changing under
      real traffic — demonstrate with actual output, not assertion
- [ ] `/readyz` returns unhealthy when the DB is stopped, healthy when it's up — **prove by
      actually stopping postgres and pasting both responses**
- [ ] Error tracking captures a deliberately-triggered exception with request context; **and**
      runs cleanly with `SENTRY_DSN` unset (both paths tested)
- [ ] PII/secret scrubbing verified — show what a captured event actually contains
- [ ] `docs/OBSERVABILITY.md` written for someone with no ops background (there's no IT dept)
- [ ] Full suite green; no measurable latency regression (cite wave-35's numbers if available)

## Deliver
Report → `work/reports/wave-36/01-observability.report.md` with real output for every check
above. Commit before writing.

## Constraints
- Time budget: 150 min
- New dependencies are fine here but list them explicitly with justification
- Everything must degrade gracefully when unconfigured
- Allowed: file edit, git, docker, pytest, curl
