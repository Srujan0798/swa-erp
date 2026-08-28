# Wave 35 — Gotchas

> **Source:** Harvested from `work/reports/wave-35/01-performance-load-validation.report.md` — real gotchas only, nothing invented.

## Known pitfalls

### Load validation 10–150 users
Load validation performed for 10–150 users. Results in `docs/PERFORMANCE.md`.

### Performance baseline established
The load test established a performance baseline. Before making performance-sensitive changes (DB queries, API endpoints, frontend rendering), re-run the load test and compare.

### Colima/Docker required for load tests
Load tests require a running Docker/Colima stack. Don't run them without the infrastructure.

### Results in docs/PERFORMANCE.md
Full results are in `docs/PERFORMANCE.md`, not in the wave-35 report alone.
