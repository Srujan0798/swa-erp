# Wave-33 Task 01 — Close backend coverage gaps (82% → ≥85%, no module <70%)

**Depends on wave-32** (real coverage gates must exist first). Verify `work/reports/wave-32/`
exists before starting.

## Measured baseline (2026-08-11, from an actual coverage run)

Overall **82%** — respectable, but with dangerous holes in exactly the modules that produce
client-facing output:

| Module | Coverage | Why it matters |
|---|---|---|
| `services/pdf_service.py` | **17%** | Generates client-facing PDFs — near-zero verification |
| `services/quote_service.py` | **21%** | Quotes are a core business object |
| `services/notification_service.py` | **50%** | |
| `services/task_service.py` | **58%** | |
| `services/import_service.py` | **65%** | Runs the one-time real-data migration — a bug here corrupts the client's actual data |

## Target
- Overall **≥85%**
- **No module below 70%**
- Priority order: `pdf_service` → `quote_service` → `import_service` → `task_service` →
  `notification_service` (worst first, and `import_service` weighted up because it touches real
  client data)

## Files to modify
- `tests/wave-33/` — new test modules (one per service under test)
- Application code **only** where a test reveals a genuine bug

## Files you must NOT touch
- Existing passing tests — don't rewrite them to inflate numbers
- CI config (wave-32 owns it) — except raising `--cov-fail-under` to 85 as your final step

## How to do this properly

**Use `superpowers:test-driven-development`.** Invoke the skill and follow it — this is exactly
its use case.

**Test behaviour, not lines.** The goal is confidence, not a number. A test that calls a function
and asserts nothing meaningful raises coverage and lowers trust — that's the failure mode to
avoid. For each module:
1. Read it and list what it actually promises to do.
2. Write tests for the real paths: happy path, each error branch, boundary conditions.
3. For `pdf_service`: assert on generated PDF **content** (the wave-23 report shows the codebase
   already does this — decompressing PDF streams and asserting on figures). Follow that pattern.
4. For `import_service`: use the synthetic fixtures in `tests/wave-13/fixtures/` — **never real
   client data**. Cover malformed rows, FK-resolution failures, idempotent re-runs.

**If a test surfaces a real bug — and at 17% coverage on `pdf_service` this is likely — fix the
bug and call it out prominently in your report.** Finding real defects is a better outcome for
this wave than hitting a coverage number cleanly.

## Acceptance criteria
- [ ] `pytest tests/ -q --cov=src/backend --cov-report=term-missing` → **≥85% overall**
- [ ] No module under 70% (paste the full coverage table in the report)
- [ ] All new tests assert on real behaviour — report must state, per module, *what behaviour* is
      now covered that wasn't
- [ ] Any bug found is fixed and documented (or explicitly reported if out of scope)
- [ ] `--cov-fail-under` raised to 85 in `pyproject.toml` as the final step
- [ ] Full suite green, zero failures; `ruff` + `mypy` still clean (wave-32's gates)

## Deliver
Report → `work/reports/wave-33/01-backend-coverage.report.md`. Include the before/after coverage
table, per-module behaviour summary, and every bug found. Commit before writing.

## Constraints
- Time budget: 180 min
- **Do not write assertion-free tests to move the number.** If you can't meaningfully test
  something in budget, say so — an honest 83% beats a hollow 87%.
- Allowed: file edit, git, pytest, ruff, mypy
