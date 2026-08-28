# Wave 33 — Gotchas

> **Source:** Harvested from `work/reports/wave-33/` — real gotchas only, nothing invented.

## Known pitfalls

### Backend coverage ≥85%
86% overall achieved; 5 target services ≥70%. Coverage was done in 3 tasks (01, 02 redo, 03 remaining).

### Coverage gaps remain
Some services are below the 70% target. Check `work/reports/wave-33/` for which services passed and which fell short.

### Test infrastructure: import-mode=importlib
`--import-mode=importlib` is required for wave-33 test collection (see pyproject.toml). Don't remove it — test collection breaks without it.

### conftest.py mutable structures warning
`tests/wave-33/test_pdf_service.py` has module-level mutable structures (possible shared state). FM-10 warning. Be careful with shared mutable state in test modules.
