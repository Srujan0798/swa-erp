# Wave-41 Task 01 — T2 operational layer

Adaptoid tier upgrade T1 → T2 (§1.5). This repo runs a real consultancy's operations on-prem with **no IT department** (Viraj confirmed) — when something breaks there is nobody to diagnose it. That makes operational docs load-bearing, not ceremony.

## Files you own (touch nothing else)
- `docs/operational/OBSERVABILITY.md`
- `docs/operational/PERFORMANCE_SLOS.md`
- `docs/operational/INCIDENT_RESPONSE_PLAYBOOK.md`
- `docs/operational/PRODUCTION_WALKTHROUGH.md`
- `docs/operational/SECURITY_PERIMETER_GUIDE.md`
- `docs/operational/DATA_INTAKE_PROTOCOL.md`
- `docs/audits/2026-08-28-baseline.md`
- `prometheus.yml`
- `docker-compose.dev.yml`
- `.github/workflows/perf_regression.yml` (the ONLY workflow file you may touch)

## Ground truth to build on (do NOT invent)
- Observability already EXISTS: `src/backend/core/metrics.py` (Prometheus), `src/backend/core/errors.py` (env-gated Sentry + PII scrubbing), `src/backend/api/health.py` (`/healthz` liveness, `/readyz` checks DB + Redis + migrations-at-head). There is already a `docs/OBSERVABILITY.md` — **move/merge it into `docs/operational/` with `git mv`, do not duplicate it.**
- Real load numbers exist in `docs/PERFORMANCE.md` and `docs/performance-runs/` — 10/50/100/150 concurrent users measured on a **dev machine**, p95 ≈ 29–130ms. Derive SLOs from these actual figures; do not invent targets.
- Known environmental coupling: `/readyz` returns 503 when Redis is absent, which makes 2 tests fail on machines without Docker. Document this in the walkthrough.

## The work
Templates are in `ADAPTOID-LITE.md` §4.5 (observability), §4.6 (SLOs), §4.7 (incident playbook), §4.4 (audit), §4.19 (prometheus), §4.17 (compose overrides).

Write for someone with **no ops background** — that is the literal audience. Plain language, concrete commands, no unexplained jargon.

- **PERFORMANCE_SLOS.md** — every target traceable to `docs/PERFORMANCE.md`. State plainly that measurements are dev-machine, and the client's Windows Server is materially larger and untested.
- **INCIDENT_RESPONSE_PLAYBOOK.md** — real scenarios for this stack: Postgres down, Redis down (and its `/readyz` effect), Celery queue stuck, JWT secret rotation, disk full from `uploads/`.
- **PRODUCTION_WALKTHROUGH.md** — what a healthy system looks like: which containers, which ports (3100/8100 dev), what `/healthz` vs `/readyz` should return.
- **SECURITY_PERIMETER_GUIDE.md** — build from what wave-37 actually fixed (path traversal, insecure-key denylist, hourly-rate settings) plus the real auth model: JWT HS256, tokens in localStorage, RBAC roles.
- **DATA_INTAKE_PROTOCOL.md** — the real Excel import path (`src/backend/services/import_service.py`, `docs/REAL_DATA.md`).
- **`docs/audits/2026-08-28-baseline.md`** — per §4.4. Findings must come from `results/metrics.json` if wave-40 has landed, else from commands you run. **Do not hand-type metrics.**
- **`prometheus.yml`** — scrape targets matching real service names in `docker-compose.yml`.
- **`docker-compose.dev.yml`** — hot-reload overrides; must actually work with the existing compose file.
- **`perf_regression.yml`** — run `tests/performance/` and fail on regression past the SLO minimums.

## Acceptance criteria
- [ ] `docker-compose -f docker-compose.yml -f docker-compose.dev.yml config` validates — paste output
- [ ] `promtool check config prometheus.yml` passes (or note promtool unavailable and validate YAML syntax instead)
- [ ] Every SLO number cites its source line in `docs/PERFORMANCE.md`
- [ ] `git log --follow docs/operational/OBSERVABILITY.md` shows history from the old path (proves `git mv`)
- [ ] No metric hand-typed that contradicts `results/metrics.json`

## Deliver
`work/reports/wave-41/01-operational-layer.report.md`. Commit before writing it.

## Constraints
- Time budget: 150 min · commit per document
- Zero application-code changes
