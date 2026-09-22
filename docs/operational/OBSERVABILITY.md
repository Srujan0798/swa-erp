# SWA ERP — Observability (as built)

> Filled this seal session from live code. Replaces the previous 85-byte git-error stub.

## What is real (verified in code)

| Signal | Implementation | Path |
|--------|----------------|------|
| Structured logs | `structlog` on request middleware → stdout → Docker | `src/backend/core/middleware.py` |
| Request ID | `X-Request-ID` set/matched on API | `src/backend/core/middleware.py` |
| Metrics | Prometheus at `/metrics` **requires auth** | wave-50; gated in deps/middleware |
| Liveness | `GET /healthz` | `src/backend/api/health.py` |
| Readiness | `GET /readyz` — Postgres + Redis + migration head | `src/backend/api/health.py` |
| Error tracking | Sentry optional via `SENTRY_DSN` (`sentry_sdk`) | `src/backend/core/errors.py` |
| Audit trail | Append-only `audit_log` on mutations | services + `audit_service` |
| Background jobs | Celery worker (compose `worker`) | `src/backend/workers/` |

## What is not built

- fluentd / log shipping to a central collector
- Distributed tracing (OTel)
- Multi-host dashboards (single compose stack)

## How to verify

```bash
curl -fsS http://localhost:8100/healthz
curl -fsS http://localhost:8100/readyz   # needs Postgres + Redis
# /metrics requires a valid JWT (see docs/flows/02_auth_rbac.md)
```

## Alerting stance (no IT department)

1. `readyz` failing → stack is down; restart compose services.
2. Repeated 5xx in logs → check `X-Request-ID` chain + Sentry if DSN set.
3. Job stuck → `docker compose ps worker` + Redis queue depth.
