# Seal truth report — session 2026-09-22

Independent verification: commands run this session. Failures listed by node id. Coverage from this run’s TOTAL lines. Known pre-existing issues: listed below.

## Environment

- Docker: **UP** (postgres, redis, minio, backend, worker healthy)
- Date: 2026-09-22 (UTC)

### readyz (resolved this session)

- Was **503** `migrations pending: current=0043, head=0042` — 4h-old backend image lacked `0043_idempotency_composite_pk.py` (host DB already at 0043).
- Fix: `docker compose build backend worker migrate && docker compose up -d backend worker`.
- Now: `GET /readyz` → **HTTP 200** `{"status":"ok","checks":{"db":"ok","redis":"ok","migrations":"ok"}}`.

## Backend static

| Gate | Command | Exit | Result |
|------|---------|------|--------|
| Ruff | `python3 -m ruff check src/backend/` | 0 | All checks passed |
| Black | `python3 -m black --check src/backend/` | 0 | 163 files unchanged |
| Mypy (CI) | `python3 -m mypy src/backend/ --explicit-package-bases` | 0 | clean, 162 files (this session) |

## Backend tests

```text
CLAIM: 673 passed, 2 skipped, 0 failed
COMMAND: python3 -m pytest tests/ -q
OUTPUT: 184.34s this session
DATE: 2026-09-22
```

Coverage TOTAL (this session, clean re-run line 479): `TOTAL                                                                           9171   1543    83%`  
COMMAND: `python3 -m pytest tests/ -q --cov=src/backend --cov-report=term`  
OUTPUT: `work/reports/seal/backend-cov-raw.txt` (**673 passed, 2 skipped, 0 failed**, 168.65s, exit 0)  
DATE: 2026-09-22

Prior cov attempt in same session had 3 sqlalchemy env errors (670/2/3, TOTAL 9163 1491 84%) — superseded by the clean run above.

## Frontend

| Gate | Result |
|------|--------|
| tsc --noEmit | pass |
| eslint | pass |
| vitest run --coverage | **0 failed** |

```text
CLAIM: functions 62.28% (862/1384), statements 65.73%, branches 59.1%, lines 67.11%
COMMAND: npx vitest run --coverage
OUTPUT: this session
DATE: 2026-09-22
```

## Migrations

```text
CLAIM: single head 0043
COMMAND: python3 -m alembic -c src/backend/alembic.ini heads
OUTPUT: 0043 (head)
DATE: 2026-09-22
```

**Resolved:** `HANDOFF.md` now documents head `0043` (was stale `0042`).

## CI workflows

- `evals.yml`: `continue-on-error: true` **by design** (documented in file header).
- `perf_regression.yml`: `curl … || true` on readyz — non-fatal probe; document if used as quality gate.

## Phase 0 artifacts

| Artifact | Path | Status |
|----------|------|--------|
| MD census | `work/reports/seal/MD_CENSUS.md` | written (169 files) |
| Graphify queries | `work/reports/seal/GRAPHIFY.md` | written |
| Graph report | `graphify-out/GRAPH_REPORT.md` | present |
| Archives | `attic/dispatch-24h/`, `attic/final-close/`, `docs/historical/` | moved this session, **0 deletes** |
| OBSERVABILITY | `docs/operational/OBSERVABILITY.md` | filled |
| SCOPE roles | `docs/SCOPE_GUARD.md` | reconciled to `core/roles.py` |
| Protocol | `docs/SEAL_PROTOCOL.md` | this document’s parent |

## NOT verified this session (do not claim)

- Playwright director-path seal traces  
- Sheet-parity matrix completion  
- Production deploy / Viraj server  
- Excel freeze migration on client production data  

## Open external / user

| ID | Item |
|----|------|
| O1 | Rotate GitHub PAT |
| O2 | Approve project postgres MCP (`claude` in repo) |
| O3 | 195 historical secrets remediation |
| EXT | Viraj 8 server facts, Excel freeze, company-server deploy |
