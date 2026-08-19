# Performance Testing with Locust

This directory contains load testing scripts using [Locust](https://locust.io/) to validate the performance claims of the SWA ERP system.

## Test Profile

The load test models realistic user journeys based on actual SWA staff workflows (from `resources/MEETINGS_MASTER.md`):

| User Type | Weight | Description |
|-----------|--------|-------------|
| PM (Project Manager) | 50% | Full access - dashboards, project CRUD, client management, time approval, exports |
| Designer | 30% | Project execution - tasks, time entries, documents, timesheets |
| Viewer | 20% | Read-only - dashboards, project/client lists and details |

**Request Distribution:**
- 60% reads (dashboards, lists, detail views)
- 25% periodic writes (create inquiry, log time, issue token, document ref)
- 10% heavy operations (PDF export, report generation)
- 5% authentication (login/refresh)

## Prerequisites

1. Docker Compose stack running (`make dev` or `make dev-services`)
2. Test data seeded in the database (run the seed script in `scripts/seed_dev.py` or use `make seed-dev`)

## Running the Load Test

### Option 1: Using the Make target (recommended)

```bash
# Start the stack first
make dev

# In another terminal, run the load test
make load-test USERS=100 SPAWN_RATE=10 RUN_TIME=5m
```

### Option 2: Direct Locust command

```bash
# Run headless (CI mode)
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8100 \
  --users=100 \
  --spawn-rate=10 \
  --run-time=5m \
  --headless \
  --html=load-test-report.html \
  --csv=load-test-results

# Run with Web UI
locust -f tests/performance/locustfile.py --host=http://localhost:8100
# Then open http://localhost:8089 in browser
```

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--users` | Peak concurrent users | 10 |
| `--spawn-rate` | Users spawned per second | 1 |
| `--run-time` | Test duration (e.g., 30s, 5m, 1h) | 1m |
| `--headless` | Run without Web UI | N/A |
| `--html` | Generate HTML report | N/A |
| `--csv` | Generate CSV results | N/A |

## Test Stages

The standard validation runs tests at these concurrency levels:

1. **10 users** (baseline) - 2 minutes
2. **50 users** - 3 minutes
3. **100 users** (target claim) - 5 minutes
4. **150 users** (stress) - 3 minutes

Run each stage separately to identify the degradation point:

```bash
# Stage 1: 10 users
make load-test USERS=10 SPAWN_RATE=2 RUN_TIME=2m

# Stage 2: 50 users
make load-test USERS=50 SPAWN_RATE=5 RUN_TIME=3m

# Stage 3: 100 users (the claim)
make load-test USERS=100 SPAWN_RATE=10 RUN_TIME=5m

# Stage 4: 150 users (find breaking point)
make load-test USERS=150 SPAWN_RATE=10 RUN_TIME=3m
```

> **Status (wave-35, 2026-08-19):** **all four stages (10, 50, 100, 150 users)** have been run —
> results in `docs/PERFORMANCE.md` (at 100 users: p95 ≈ 51 ms; at 150 users: p95 ≈ 130 ms, no
> server 5xx at any level). A load test on the client's Windows Server is **not yet done**; the
> "100+ concurrent users" figure is IT's claim about the server and must not be presented as
> verified on the client's hardware until a load test runs there.

## Interpreting Results

### Key Metrics to Watch

| Metric | Healthy Target | Warning | Critical |
|--------|---------------|---------|----------|
| **Error Rate** | < 0.1% | 0.1-1% | > 1% |
| **p50 Latency** | < 200ms | 200-500ms | > 500ms |
| **p95 Latency** | < 500ms | 500-1000ms | > 1000ms |
| **p99 Latency** | < 1000ms | 1000-2000ms | > 2000ms |
| **Throughput** | > 50 req/s | 20-50 req/s | < 20 req/s |

### Locust Output

Key columns in the statistics table:

- **Name**: Endpoint group name
- **# reqs**: Total requests
- **# fails**: Failed requests
- **Avg**: Average response time (ms)
- **Min/Max**: Min/Max response time
- **Median (p50)**: 50th percentile
- **p95/p99**: 95th/99th percentiles
- **RPS**: Requests per second

### Failure Analysis

Common failure patterns:

1. **401 Unauthorized**: Token expiry - increase token TTL or add refresh logic
2. **429 Too Many Requests**: Rate limiting - check `DISABLE_AUTH_RATE_LIMIT`
3. **500 Internal Server Error**: Application bugs - check backend logs
4. **503 Service Unavailable**: Database connection pool exhausted - increase pool size
5. **Timeout**: Slow queries - check for N+1 or missing indexes

## Environment Caveats

**This test runs on a development machine, not the client's 128GB Windows Server.**

Typical dev environment:
- MacBook Pro (Apple Silicon) or similar
- Docker containers sharing host resources
- PostgreSQL and Redis in containers (not tuned)
- No dedicated load generator hardware

**Do not extrapolate these numbers to the client's server.** Present as: "Measured on X, the client's server is materially larger."

## Documenting Results

After running tests, record results in `docs/PERFORMANCE.md` with:

1. Test environment (hardware, OS, Docker version)
2. Methodology (user profile, stages, duration)
3. Results table per stage (p50/p95/p99, throughput, error rate)
4. Concurrency level where degradation begins
5. Any N+1 queries or missing indexes identified
6. Before/after numbers if fixes applied
7. Corrected claims for any docs stating "100+ concurrent users"

## Continuous Integration

For CI integration, use headless mode with JUnit XML output:

```bash
locust -f tests/performance/locustfile.py \
  --host=http://backend:8000 \
  --users=50 \
  --spawn-rate=5 \
  --run-time=2m \
  --headless \
  --junit-xml=locust-junit.xml
```

Then set pass/fail thresholds in your CI pipeline based on the metrics above.