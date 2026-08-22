# Wave-33 Task 02 — Backend coverage redo

**Status:** PARTIAL — 3 of 5 target modules done and verified. `task_service` and
`notification_service` still need coverage; not attempted before the session ran out of budget.

## What's real (independently verified by the orchestrator, 2026-08-22)

```
python3 -m pytest tests/wave-33/ -q --cov=src.backend.services.pdf_service \
  --cov=src.backend.services.quote_service --cov=src.backend.services.import_service \
  --cov-report=term
```

```
Name                                     Stmts   Miss  Cover
------------------------------------------------------------
src/backend/services/import_service.py     561    152    73%
src/backend/services/pdf_service.py         96      0   100%
src/backend/services/quote_service.py      125      4    97%
------------------------------------------------------------
TOTAL                                      782    156    80%
58 passed in 6.77s
```

| Module | Baseline | Now | Target | Status |
|---|---|---|---|---|
| `services/pdf_service.py` | 17% | **100%** | ≥70% | ✅ met |
| `services/quote_service.py` | 21% | **97%** | ≥70% | ✅ met |
| `services/import_service.py` | 65% | **73%** | ≥70% | ✅ met |
| `services/task_service.py` | 58% | 58% (untouched) | ≥70% | ❌ not attempted |
| `services/notification_service.py` | 50% | 50% (untouched) | ≥70% | ❌ not attempted |

Test files: `tests/wave-33/test_pdf_service.py`, `tests/wave-33/test_quote_service.py`,
`tests/wave-33/test_import_service.py` — all exist, all pass, verified by running them directly.

## What was fixed to make verification possible
- `pyproject.toml`: added `--import-mode=importlib` to `addopts` (needed to avoid a module-name
  collision when collecting the new wave-33 test files alongside the rest of the suite).
- `requirements.txt`: added `pypdf==5.1.0` — `test_pdf_service.py` imports it to decode and
  assert against real PDF content; it was missing from dependencies, causing a collection error.

## Honest status
This wave's original ≥85% overall / no-module-below-70% goal is **not met** — `task_service` and
`notification_service` remain below target. The 3 modules that were tackled are genuinely done
(coverage numbers above independently reproduced, not self-reported). Recommend a follow-up
dispatch scoped to just `task_service` + `notification_service` rather than re-running all 5.

## Commands run (this verification pass)
```bash
python3 -m pytest tests/wave-33/ -q   # 58 passed
python3 -m pytest tests/wave-33/ -q --cov=src.backend.services.pdf_service \
  --cov=src.backend.services.quote_service --cov=src.backend.services.import_service \
  --cov-report=term   # numbers above
```
