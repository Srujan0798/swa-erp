# Active Work — waves 32-39

Live wave tracking. Waves 1-31 (shipped history) live in
[`work/ARCHIVE.md`](ARCHIVE.md). Every wave appears in exactly one of the two files.

## Dependency order

```
wave-32 (real CI gates) ── runs first, alone; everything below depends on it
  ├── wave-33 (backend coverage)      ── depends on 32; parallel-safe with 34/35
  ├── wave-34 (frontend test suite)   ── depends on 32; parallel-safe with 33/35
  └── wave-35 (load validation)       ── depends on 32; parallel-safe with 33/34
        └── wave-36 (observability)   ── depends on 32; best run after 35
              └── wave-37 (independent review) ── depends on 32,33,34,35
                    └── wave-38 (submission package) ── runs last; depends on 32-37

wave-39 (repo organization) ── current; organization only, touches zero code
```

## Wave table

| # | Purpose | Status | Depends on | Brief | Report |
|---|---|---|---|---|---|
| 32 | Make CI real (remove fake gates) + security scanning | **SHIPPED** ✅ | — | [`work/wave-32/`](wave-32/) | [`work/reports/wave-32/`](reports/wave-32/) |
| 33 | Close backend coverage gaps (82% → ≥85%) | **IN-FLIGHT** | 32 | [`work/wave-33/`](wave-33/) | [`work/reports/wave-33/`](reports/wave-33/) |
| 34 | Build a real frontend test suite (≥60% coverage) | **IN-FLIGHT** | 32 | [`work/wave-34/`](wave-34/) | [`work/reports/wave-34/`](reports/wave-34/) |
| 35 | Load-test validation (10/50/100/150 users) | **SHIPPED** ✅ | 32 | [`work/wave-35/`](wave-35/) | [`work/reports/wave-35/`](reports/wave-35/) |
| 36 | Production observability (metrics + error tracking) | **IN-FLIGHT** | 32, best after 35 | [`work/wave-36/`](wave-36/) | — (report lost — never committed) |
| 37 | Independent adversarial review (multi-agent) | **QUEUED** | 32, 33, 34, 35 | [`work/wave-37/`](wave-37/) | — |
| 38 | Professional submission package | **QUEUED** | 32-37 | [`work/wave-38/`](wave-38/) | — |
| 39 | Repo organization (this wave — make the repo legible) | **IN-FLIGHT** | none (docs only) | [`work/wave-39/`](wave-39/) | — (this wave's report is written on completion) |

## Status notes

- **32**: real gates in CI; wave-33+ evidence depends on it having landed.
- **33**: brief dispatched twice (`01-backend-coverage` then `02-backend-coverage-redo`);
  report on file but marked **NOT DONE** by the orchestrator's independent verification.
- **34**: task 01 report confirms **386 frontend tests passing** (hooks at 100%); task 02
  (`02-frontend-page-coverage`, pages at 1.6% statements) was dispatched with wave-39 — so the
  wave is **in-flight**, not shipped.
- **35**: shipped — `docs/PERFORMANCE.md` + raw runs archived to `docs/performance-runs/` (wave-39).
- **36**: code merged (`metrics.py`, `/metrics`, error tracking) but its report was **never
  committed** — `work/reports/wave-36/` does not exist. Re-reporting is a known gap.
- **37 / 38**: briefs written and dispatched but not yet run; they must not run before their
  dependencies above have landed and been verified.
- **39**: this wave — organization only; no code changes.

If a wave is missing from both tables, that is a bug in this file — every wave 1-38 must
appear in exactly one.