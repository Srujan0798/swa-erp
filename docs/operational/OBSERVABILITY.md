# Observability — Metrics, Error Tracking, Health Checks

This document explains what observability data SWA ERP collects, how to read it, and how to set up alerting. Written for a team with **no dedicated IT/ops department** — the system must be self-explanatory.

> **Operational companion docs (read these alongside this one):**
> - [`PRODUCTION_WALKTHROUGH.md`](PRODUCTION_WALKTHROUGH.md) — what a healthy system looks like
> - [`PERFORMANCE_SLOS.md`](PERFORMANCE_SLOS.md) — speed targets and where they come from
> - [`INCIDENT_RESPONSE_PLAYBOOK.md`](INCIDENT_RESPONSE_PLAYBOOK.md) — what to do when something breaks
> - [`SECURITY_PERIMETER_GUIDE.md`](SECURITY_PERIMETER_GUIDE.md) — what is protected and how
> - [`DATA_INTAKE_PROTOCOL.md`](DATA_INTAKE_PROTOCOL.md) — how client Excel sheets get imported

> **Heads-up on `/readyz` and Redis:** `/readyz` returns HTTP `503` when Redis is unreachable
> (or Postgres is down, or migrations are not at head). On machines without Docker (or with Redis
> stopped), two health-related tests will fail — that is expected, not a code bug. See
> `INCIDENT_RESPONSE_PLAYBOOK.md` → "Redis down".

---

## What We Have (Implemented in Wave-36)

| Capability | Status | Endpoint / Config |
|------------|--------|-------------------|
| **Structured Logging** | ✅ Done (Wave-1) | `structlog` with `X-Request-ID` correlation |
| **Prometheus Metrics** | ✅ Done | `GET /metrics` (internal only) |
| **Error Tracking (Sentry)** | ✅ Done | Env-gated via `SENTRY_DSN` |
| **Health Checks** | ✅ Done | `GET /healthz` (liveness), `GET /readyz` (readiness) |

---

## 1. Structured Logging

**What:** Every request gets a unique `X-Request-ID` header. All log lines include this ID so you can trace a request across services.

**Where:** Logs go to stdout (Docker captures them). In production, pipe to your log aggregator (Loki, ELK, etc.).

**Example log line:**
```
2026-08-19T14:30:15.123Z INFO request_id=abc-123 method=GET path=/api/projects/123 status=200 duration_ms=45
```

**How to use:**
- Search logs by `request_id` to see the full lifecycle of a request
- Correlate with Sentry events (they also include `request_id`)

---

## 2. Prometheus Metrics (`/metrics`)

**Endpoint:** `GET /metrics` — **NOT exposed publicly**. In production, bind to localhost or protect with auth.

**What's collected:**

### HTTP Request Metrics
| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | method, endpoint, status_class | Total requests (status_class = 2xx, 3xx, 4xx, 5xx) |
| `http_request_duration_seconds` | Histogram | method, endpoint | Request latency |
| `http_requests_in_flight` | Gauge | method, endpoint | Currently processing requests |

### Database Metrics
| Metric | Type | Description |
|--------|------|-------------|
| `db_pool_size` | Gauge | Connection pool size |
| `db_pool_checked_out` | Gauge | Connections in use |
| `db_pool_overflow` | Gauge | Overflow connections |

### Celery Metrics
| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `celery_queue_depth` | Gauge | queue | Tasks waiting in queue |
| `celery_tasks_total` | Counter | queue, status | Tasks processed (status: success/failure/retry) |

### Business Metrics
| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `failed_logins_total` | Counter | — | Failed login attempts |
| `http_5xx_total` | Counter | endpoint | Server errors by endpoint |

**How to scrape:**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'swa-erp'
    static_configs:
      - targets: ['backend:8000']  # internal Docker network
    metrics_path: '/metrics'
```

**Key alerts to set up:**
```yaml
# High error rate
- alert: High5xxRate
  expr: rate(http_5xx_total[5m]) > 0.01
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "High 5xx error rate on {{ $labels.endpoint }}"

# Database pool exhaustion
- alert: DBPoolExhausted
  expr: db_pool_checked_out / db_pool_size > 0.9
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Database connection pool 90% utilized"

# Celery queue backlog
- alert: CeleryQueueBacklog
  expr: celery_queue_depth > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Celery queue {{ $labels.queue }} has {{ $value }} pending tasks"

# Failed login spike
- alert: FailedLoginSpike
  expr: rate(failed_logins_total[5m]) > 10
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "Unusual failed login rate"
```

---

## 3. Error Tracking (Sentry)

**Configuration:** Set `SENTRY_DSN` environment variable. **If not set, runs in no-op mode** — zero overhead, no crashes, no data sent.

**What's captured:**
- Unhandled exceptions with full stack trace
- Request context (method, URL, headers, client IP)
- `X-Request-ID` for log correlation
- Custom context from business logic

**PII/Secret Scrubbing:**
Before any event is sent, the following are redacted:
- Authorization headers, cookies, API keys
- Password, secret, token fields in exception frames
- Credit card, PAN, GSTIN, bank account numbers
- Any field containing sensitive keywords

**To verify scrubbing works:**
1. Set `SENTRY_DSN` to a test project
2. Trigger an error with sensitive data
3. Check the Sentry event — sensitive fields show `[REDACTED]`

**To test locally without sending data:**
```bash
# Don't set SENTRY_DSN — runs in no-op mode
make dev
# Trigger an error (e.g., 500 endpoint)
curl http://localhost:8100/api/debug/crash
# Check logs — no crash, no network call to Sentry
```

---

## 4. Health Endpoints

### `/healthz` — Liveness Probe
- **Purpose:** "Is the process alive?"
- **Cost:** Near-zero (no I/O)
- **Returns:** `{"status": "ok"}`
- **Use for:** Kubernetes liveness probe, Docker healthcheck

### `/readyz` — Readiness Probe
- **Purpose:** "Can the app serve traffic?"
- **Checks:**
  1. **Database** — `SELECT 1` succeeds
  2. **Redis** — `PING` succeeds
  3. **Migrations** — Current revision = head revision
- **Returns:** 
  - `200 OK` + `{"status": "ok", "checks": {...}}` if all healthy
  - `503 Service Unavailable` + `{"status": "error", "checks": {...}}` if any fail
- **Use for:** Kubernetes readiness probe, load balancer health check

**Example healthy response:**
```json
{
  "status": "ok",
  "checks": {
    "db": "ok",
    "redis": "ok",
    "migrations": "ok"
  }
}
```

**Example unhealthy response (DB down):**
```json
{
  "status": "error",
  "checks": {
    "db": "error: connection refused",
    "redis": "ok",
    "migrations": "ok"
  }
}
```

---

## 5. How to Verify (Wave-36 Acceptance Checks)

### Verify `/metrics` works
```bash
curl http://localhost:8100/metrics | head -50
# Should show Prometheus format output with http_requests_total, etc.

# Make some requests, then check counters increased
curl http://localhost:8100/api/dashboard/executive -H "Authorization: Bearer <token>"
curl http://localhost:8100/metrics | grep http_requests_total
```

### Verify `/readyz` detects DB down
```bash
# Stop postgres
docker-compose stop postgres

# Check readyz
curl http://localhost:8100/readyz
# Should return 503 with db: "error: ..."

# Restart postgres
docker-compose start postgres
# Wait for healthy, then:
curl http://localhost:8100/readyz
# Should return 200 with all checks "ok"
```

### Verify Sentry captures errors (with DSN)
```bash
export SENTRY_DSN="https://test@test.ingest.sentry.io/123"
docker-compose restart backend

# Trigger an error
curl -X POST http://localhost:8100/api/debug/crash -H "Authorization: Bearer <token>"

# Check Sentry dashboard — should show the exception with request_id
```

### Verify Sentry no-op without DSN
```bash
unset SENTRY_DSN
docker-compose restart backend

# Trigger an error
curl -X POST http://localhost:8100/api/debug/crash -H "Authorization: Bearer <token>"

# Should return 500 but NOT crash the app, no network call to Sentry
# Check logs — no "Sentry" errors
```

### Verify PII scrubbing
```bash
export SENTRY_DSN="https://test@test.ingest.sentry.io/123"
docker-compose restart backend

# Trigger error with sensitive data
curl -X POST http://localhost:8100/api/debug/crash-with-pii \
  -H "Authorization: Bearer <token>" \
  -d '{"password": "secret123", "api_key": "sk-live-xxx"}'

# Check Sentry event — password and api_key should be [REDACTED]
```

---

## 6. Production Checklist

Before deploying to the client's Windows Server:

- [ ] Set `SENTRY_DSN` in production environment
- [ ] Configure Prometheus to scrape `/metrics` (internal network only)
- [ ] Set up alert rules (see §2)
- [ ] Configure log aggregation (stdout → Loki/ELK)
- [ ] Add `/readyz` to load balancer health checks
- [ ] Add `/healthz` to Docker/container orchestrator health checks
- [ ] Document runbook: "What to do when alert X fires"

---

## 7. Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `/metrics` returns 404 | Metrics not installed | Check `lifespan` in `main.py` calls `setup_metrics(app)` |
| Sentry not capturing | `SENTRY_DSN` not set | Set `SENTRY_DSN` env var; restart app |
| `/readyz` always 503 | DB/Redis not reachable | Check `DATABASE_URL`, `REDIS_URL`; verify network |
| Migration check fails | DB not at head | Run `alembic upgrade heads` |
| High memory in metrics | Too many unique endpoints | Increase `should_group_status_codes`, limit cardinality |

---

## 8. What's Not Done (Target State)

| Feature | Status | Notes |
|---------|--------|-------|
| Distributed tracing (Jaeger/Zipkin) | ❌ Not started | Add if request flow debugging needed |
| Custom dashboards (Grafana) | ❌ Not started | Build after Prometheus is scraped |
| Log-based alerting (Loki) | ❌ Not started | Add if log patterns need alerting |
| Uptime monitoring (external) | ❌ Not started | Use Pingdom, UptimeRobot, etc. |

**Rule:** We do not claim these exist. They are explicitly "target state" for future waves.