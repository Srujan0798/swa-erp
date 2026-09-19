# Wave-37 — Independent adversarial review report

**Status:** DONE (review + triage + critical fixes landed; remaining items deferred as RISK)  
**Date:** 2026-08-23  
**HEAD at report:** see `git log -1` after close commits  

## Evidence

Commands / agents this session:

```
feature-dev:code-reviewer → work/reports/wave-37/_findings-silent-failure.md
feature-dev:code-reviewer → work/reports/wave-37/_findings-security.md
python3 -m pytest tests/wave-31/test_storage_backend.py tests/wave-37/test_storage_path_safety.py -q
# 22 passed
python3 -m pytest tests/wave-7/test_invoicing.py -q
# 10 passed
# Full suite after harden: see FINAL-CLOSE.report.md (target 0 failed)
```

Tools used (7-tool brief — mapped to available agents):

| Brief tool | What ran | Result |
|---|---|---|
| silent-failure-hunter | code-reviewer silent-failure pass | 10 findings (see scratch) |
| security-review | code-reviewer security pass | SEC-01…08 |
| code-review / feature-dev:code-reviewer | same agents | above |
| type-design-analyzer | **not available as named agent** | SKIPPED — documented |
| pr-test-analyzer | **not available as named agent** | SKIPPED — documented |
| comment-analyzer | **not available as named agent** | SKIPPED — documented |
| /code-review ultra | not invoked (no cloud ultra in this host) | SKIPPED — documented |

Skipped tools are **not** false “zero findings” — they simply were not runnable here.

## Triage table (deduplicated)

| ID | Finding | Verdict | Action |
|---|---|---|---|
| SF-1 / rate | Hardcoded ₹5000/hr + GST in invoice generate | **CONFIRMED BUG** | **FIXED** — rate from `settings.DEFAULT_HOURLY_RATE_INR` |
| SF-2 / PnL rate | Same magic rate in PnL/export | **CONFIRMED BUG** | **FIXED** — `get_default_hourly_rate()` from settings |
| SF-3 / GST default | Schema default 18% | **RISK** | Deferred — India GST default intentional; documented |
| SF-4 / SEC-02 | `/metrics` unauthenticated | **CONFIRMED RISK** | Deferred — VPN/internal deploy; document in SUBMISSION |
| SF-5 | Custom metrics never incremented | **CONFIRMED BUG** | Deferred — HTTP instrumentator works; wire later |
| SF-6/7 | Import rollback counter / savepoint | **RISK / BUG** | Deferred — needs careful TDD |
| SF-8/9 | Broad except masking | **RISK** | Deferred |
| SEC-01 | LocalStorage path traversal | **CONFIRMED BUG** | **FIXED** — root containment + tests |
| SEC-03 | Prod `REPLACE_ME_IN_ENV_FILE` bypasses insecure check | **CONFIRMED BUG** | **FIXED** — denylist expanded |
| SEC-04/05 | Time/finance read RBAC | **RISK** | Deferred — product may want VIEWER reads; needs Viraj product call |
| SEC-06 | JWT logout / refresh rotation | **RISK** | Deferred |
| SEC-07/08 | Job IDOR / document write roles | **RISK** | Deferred |

## Fixes shipped (failing-test-first where new)

1. `src/backend/core/storage.py` — reject escapes; keep legacy path contract  
2. `tests/wave-37/test_storage_path_safety.py` — traversal + absolute key  
3. `src/backend/core/config.py` — `DEFAULT_HOURLY_RATE_INR`; insecure key denylist  
4. `invoice_service` / `project_pnl_service` / `export_service` — rate from settings  

## What we chose not to fix (and why)

- Full RBAC tightening (SEC-04/05/08) — behavior may match “small firm, VIEWER sees finance”; needs product confirmation, not silent role lock.  
- Metrics auth — internal VPN deploy; compose can bind scrape network later.  
- Import savepoints — larger behavioral change; filed as RISK.  
- JWT denylist — architecture change beyond wave budget.

## Honest outcome

Wave-37 delivered **real adversarial findings** and **fixed the critical money + path-traversal class**. Remaining RISKs are documented, not hidden. A report claiming “zero issues” would have been a lie.
