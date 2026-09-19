# Performance Runs — raw Locust evidence

This directory is the canonical home for raw Locust load-test output
(`load-test-report-<timestamp>.html` + `load-test-results-<timestamp>_*.csv`),
moved here from the repo root in wave-39 so the top level stays legible. The
published analysis lives in [`docs/PERFORMANCE.md`](../PERFORMANCE.md).

## Run index

| Timestamp | Users | Spawn rate | What it is |
|---|---|---|---|
| `20260819-200408` | 10 | 2 | Early / **broken** run — exposed a real 500 bug on project-list endpoints and harness 404s/422s (see §2). **28.6% failure rate is a since-fixed bug, not a load limit.** |
| `20260819-200957` | 10 | 2 | First fixed run — 0 5xx; remaining failures are harness 422s/404s. |
| `20260819-201658` | 10 | 2 | Harness further corrected — cleanest 10-user run (0.35% failures). |
| `20260819-201906` | 50 | 5 | First scale-up. |
| `20260819-202227` | 100 | 10 | The claimed level — answers the "100+ concurrent users" question. |
| `20260819-202748` | 150 | 10 | Stress / degradation knee. |

## Which run `docs/PERFORMANCE.md` cites

`docs/PERFORMANCE.md` walks all six runs in §3. Its headline numbers are:

- **Current 10-user number:** `20260819-201658` (the cleanest captured run).
- **First scale-up / 50-user headline:** `20260819-201906`.
- **Claim-level run:** `20260819-202227` (100 users — no 5xx, p95 ≈ 51 ms).
- **Degradation knee:** `20260819-202748` (150 users — p95 51 → 130 ms).

## About the `200408` run

The `20260819-200408` run's **28.6% failure rate was a real, then-fixed server
bug** (`GET /api/projects` 500s) plus harness errors (a nonexistent `/api/tasks`
route, two 422 payload mismatches), **not** a load limit. After the fix, the
same 10-user concurrency ran at 5.0% → 0.35% failures, all remaining failures
being test-harness payload/route mismatches. Do not cite the 28.6% as a
capacity ceiling — it was the app crashing, and it was fixed before any later
run.

## Format notes

Per run, four CSVs accompany the HTML report (Locust headless output):

- `*_stats.csv` — aggregate request statistics.
- `*_stats_history.csv` — per-second history (used to confirm peak user counts).
- `*_failures.csv` — per-endpoint failure counts.
- `*_exceptions.csv` — captured exception traces.

## Future runs

New runs should be copied here, not to the repo root. `.gitignore` now ignores
`load-test-report-*.html` and `load-test-results-*` at the top level so future
runs can't re-pollute the root.
