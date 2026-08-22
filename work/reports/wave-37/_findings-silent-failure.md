## Evidence

Command: static code review by feature-dev:code-reviewer agent (2026-08-23).
Verification: file:line citations in table below; no suite re-run claimed in this scratch file.

```
static analysis only — intermediate wave-37 scratch
```

# Wave-37 — Silent Failure / Dangerous Fallback Findings

**Scope reviewed:** `src/backend/services/`, `src/backend/api/`, `src/backend/db/repositories/`, `src/backend/core/`  
**Method:** grep + file reads for bare `except`, swallowed `Exception`, soft-vs-hard delete mismatches, fake success, hardcoded financial ratios, observability/CI theater.  
**Bar:** only citeable issues; soft_delete helpers that correctly set `deleted_at` were **not** reported.

## /metrics auth note

**`GET /metrics` is unauthenticated.** Exposed in `src/backend/main.py:103` via `_instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)` with no `Depends(get_current_user)` / basic-auth / network gate. Wave-36 tests (`tests/wave-36/test_observability.py`) call `client.get("/metrics")` without credentials and assert HTTP 200.

---

## Findings

| # | File:line | Severity | Evidence (cite) | Triage |
|---|-----------|----------|-----------------|--------|
| 1 | `src/backend/services/invoice_service.py:138`, `:160` | **CRITICAL** | `generate_from_time_entries` hardcodes `rate_per_hour = Decimal("5000.00")` and `tax_rate=Decimal("18.00")`, then creates a real invoice via `create_invoice_service`. API: `POST .../invoices/generate-from-time` (`api/invoices.py:56-77`). No per-user/project rate lookup. | **CONFIRMED BUG** — live billing invents rate + GST |
| 2 | `src/backend/services/project_pnl_service.py:23`, `:56`; `src/backend/services/export_service.py:224` | **CRITICAL** | `DEFAULT_HOURLY_RATE = Decimal("5000.00")` multiplies all billable hours for PnL time cost and financial PDF export. Same magic number as invoice path; not configurable. | **CONFIRMED BUG** — PnL/export money is fabricated |
| 3 | `src/backend/schemas/invoice.py:33`; `src/backend/models/invoice.py:24` | **HIGH** | Schema + column default `tax_rate=Decimal("18.00")`. Manual invoice create can override; generate-from-time cannot (see #1). | **RISK** — India GST default may be intentional, but coupled with #1 it becomes silent wrong-tax on time invoices |
| 4 | `src/backend/main.py:103` | **HIGH** | `/metrics` registered with no auth dependency. Prometheus text includes request paths, status classes, latency; custom counters also registered on same registry. | **CONFIRMED RISK** — unauthenticated metrics scrape |
| 5 | `src/backend/core/metrics.py:75-86`, `:141-164` | **HIGH** | Docstring claims DB pool, Celery depth, failed logins, 5xx counters. `record_failed_login`, `record_5xx`, `record_celery_task`, `update_db_pool_metrics` are **never called** anywhere else in the repo (grep only hits this file). Counters stay at 0 while HTTP instrumentator metrics work — tests only assert the latter. | **CONFIRMED BUG** — observability theater / silent zero metrics |
| 6 | `src/backend/services/import_service.py:978-987` | **HIGH** | On fatal error (incl. failed `session.commit()`), code `session.rollback()` then `result.add_error(0, f"Fatal: {e}")` but does **not** reset `result.created` / `updated` / `skipped`. Caller can see `created: N` with `ok: false` after full rollback. | **CONFIRMED BUG** — fake success counts after rollback |
| 7 | `src/backend/services/import_service.py:508-509` (and sibling row handlers `:546`, `:596`, `:644`, `:703`, `:738`, `:817`, `:877`) | **MED** | Per-row `except Exception as e: result.add_error(i, str(e))` with **no** `session.rollback()` / savepoint. A DB integrity error poisons the SQLAlchemy session; later rows cascade-fail; eventual commit raises → #6. Errors are recorded (not fully silent) but recovery is wrong. | **RISK** — needs-repro with intentional IntegrityError mid-import |
| 8 | `src/backend/api/rfqs.py:61-62` | **MED** | `except Exception as e: raise HTTPException(status_code=400, detail=str(e))` on RFQ create. Programming/DB 500s become client 400s; no logging. | **RISK** — error-class masking |
| 9 | `src/backend/services/auth_service.py:58-61` | **MED** | `refresh_access_token`: `except Exception: return None` on `decode_token` — no log/metric. API maps to 401 (`api/auth.py:45-46`). Fail-closed is correct for bad JWT; bare `Exception` also hides unexpected decode bugs. | **RISK** — swallow without observability |
| 10 | `src/backend/core/metrics.py:147-149` | **MED** | `update_db_pool_metrics`: bare `except Exception: pass`. Function is currently **uncalled** (dead), so no runtime impact today; dangerous if wired later without logging. | **RISK** — silent swallow pattern (dormant) |

---

## Explicitly checked — no high-confidence hit

| Pattern | Result |
|---------|--------|
| `soft_delete*` that hard-deletes | All named `soft_delete*` in repositories set `deleted_at` (projects, clients, tasks, quotes, invoices, etc.). |
| `TaskRepository.delete` hard-delete (`task_repo.py:87-89`) | Present but **unused**; public API uses `soft_delete()` at `:278-285`. Dead path, not active bug. |
| Document folder delete (`document_repo.py:169-180`) | Hard-deletes folder after soft-deactivating docs; folder model has no `deleted_at`. FK is `ON DELETE SET NULL` (`0010_add_documents.py:54`) — docs survive. Asymmetry by design, not a soft_delete lie. |
| Sustainability / contacts / categories hard delete | No `deleted_at` column on those models; functions named `delete_*`, not `soft_delete`. |
| Storage `FileNotFoundError: pass` (`storage.py:59-62`) | Documented no-op for missing keys. |
| `jobs.py` empty `pass` branches | Status branches with nothing to add; FAILURE still returns `error`. |
| Health `/readyz` broad except | Surfaces error strings + HTTP 503 — not silent. |
| Middleware `except Exception` | Logs then **re-raises**. |
| CI/test theater in pytest suite | Wave-36 metrics tests validate unauthenticated scrape + HTTP counters only; they do **not** assert `failed_logins_total` increments (supports finding #5). Env `skipif` for MinIO/pg_dump is legitimate, not theater. |

---

## Suggested fix order

1. **#1 / #2 / #3** — Introduce configurable hourly rate (user/project/settings) and tax source of truth; stop minting invoices/PnL from literals.  
2. **#4** — Gate `/metrics` (network policy and/or basic auth / internal-only bind).  
3. **#5** — Wire `record_failed_login` from `auth_service.login` fail path; wire 5xx/Celery/pool or delete dead counters + fix docstring.  
4. **#6 / #7** — On import fatal/rollback, zero counters or track `committed_*`; use savepoints per row for DB errors.  
5. **#8 / #9** — Narrow exception types; log unexpected failures.
