# Active Work — waves 32-39

Live wave tracking. Waves 1-31 (shipped history) live in
[`work/ARCHIVE.md`](ARCHIVE.md). Every wave appears in exactly one of the two files.

## Dependency order

```
wave-32 (real CI gates) ── SHIPPED
  ├── wave-33 (backend coverage)      ── SHIPPED
  ├── wave-34 (frontend test suite)   ── SHIPPED
  └── wave-35 (load validation)       ── SHIPPED
        └── wave-36 (observability)   ── SHIPPED (task-01 report missing; 02 + code landed)
              └── wave-37 (independent review) ── IN-FLIGHT (final close)
                    └── wave-38 (submission package) ── QUEUED after 37

wave-39 (repo organization) ── SHIPPED
```

## Wave table

| # | Purpose | Status | Depends on | Brief | Report |
|---|---|---|---|---|---|
| 32 | Make CI real (remove fake gates) + security scanning | **SHIPPED** ✅ | — | [`work/wave-32/`](wave-32/) | [`work/reports/wave-32/`](reports/wave-32/) |
| 33 | Close backend coverage gaps (82% → ≥85%) | **SHIPPED** ✅ | 32 | [`work/wave-33/`](wave-33/) | [`work/reports/wave-33/`](reports/wave-33/) |
| 34 | Build a real frontend test suite (≥60% coverage) | **SHIPPED** ✅ | 32 | [`work/wave-34/`](wave-34/) | [`work/reports/wave-34/`](reports/wave-34/) |
| 35 | Load-test validation (10/50/100/150 users) | **SHIPPED** ✅ | 32 | [`work/wave-35/`](wave-35/) | [`work/reports/wave-35/`](reports/wave-35/) |
| 36 | Production observability (metrics + error tracking) | **SHIPPED** ✅ | 32, best after 35 | [`work/wave-36/`](wave-36/) | [`work/reports/wave-36/02-post-merge-fixes.report.md`](reports/wave-36/02-post-merge-fixes.report.md) (01 never written) |
| 37 | Independent adversarial review (multi-agent) | **IN-FLIGHT** | 32, 33, 34, 35 | [`work/wave-37/`](wave-37/) | — |
| 38 | Professional submission package | **QUEUED** | 32-37 | [`work/wave-38/`](wave-38/) | — |
| 39 | Repo organization | **SHIPPED** ✅ | none (docs only) | [`work/wave-39/`](wave-39/) | [`work/reports/wave-39/`](reports/wave-39/) |

## Status notes (2026-08-23)

- **32–35, 39:** shipped and on `origin/main`.
- **33:** all 5 target modules ≥70%; overall **86%** independently verified (`5 failed / 557 passed / 1 skipped` before final-close stabilize; auth 401→403 fixes land in close).
- **34:** thresholds met; cite fresh vitest numbers (~61% stmts independent), not stale 65.86%.
- **36:** code + `02-post-merge-fixes.report.md` on main; original `01-observability.report.md` was never committed — accepted as superseded by 02 + code.
- **37 / 38:** final-close execution via `work/FINAL-CLOSE/` — do not invent parallel waves.
- **Close pack:** [`work/FINAL-CLOSE/`](FINAL-CLOSE/).

If a wave is missing from both tables, that is a bug in this file — every wave 1-39 must
appear in exactly one.
