## Evidence

Compiled from wave reports + COMPLETION-HANDOFF-VERDICT (2026-08-23). Not a pass/fail claim file.

```
sources: work/reports/wave-32..39, docs/PERFORMANCE.md, COMPLETION-HANDOFF-VERDICT.md
```

# Wave-38 — safe metrics table (paste source)

Use **only** these wordings in README / SUBMISSION / TECHNICAL_REPORT.

| Metric | Safe claim | Unsafe (banned) | Source |
|--------|------------|-----------------|--------|
| Backend overall coverage | **86%** (8702 stmts, 1201 miss) | “90%+”, invented TOTAL | `work/reports/COMPLETION-HANDOFF-VERDICT.md` (2026-08-23 clean run); `work/reports/wave-33/03-remaining-coverage.report.md` |
| Backend services | **All `services/*.py` ≥70%** | “No backend module under 70%” (false globally — 9+ non-alembic under) | Same verdict |
| Wave-33 five targets | pdf **100%**, quote **97%**, import **80%**, task **97%**, notification **100%** | — | wave-33 report 03 |
| Backend suite | **557 passed, 5 failed, 1 skipped** | “562 passed”, “0 failed” | Same |
| CI cov floor | `--cov-fail-under=82` (86% clears; aspirational 85% also met) | Claiming gate is 85% in Makefile if it isn’t | Makefile + wave-32 |
| Frontend thresholds | **60/50/60/60 met** | Claiming thresholds raised without config change | wave-34 report 02 + verdict |
| Frontend statements | **~61%** (independent) or “thresholds met” | **65.86%** without fresh `vitest --coverage` paste | Verdict (independent ~61.4%) |
| Frontend tests | Report-02: 522/0; independent excl. TaskCard: 518 pass; full IST: 521 pass / 1 fail flake | “all green always” | Verdict |
| Load concurrency | **10 / 50 / 100 / 150** users | “production verified 100+” | `docs/PERFORMANCE.md` |
| Load latency | **p95 ≈ 29–130 ms** | Dropping the range or p99 as p95 | Same |
| Load environment | **Development machine** (Docker Compose local) | Implying client Windows Server was tested | Same |
| Load errors | **No server 5xx** after run-1 fix | “0% failures” (harness 422/409 noise exists) | Same |
| CI soft-fail | **0** `\|\| true` / `continue-on-error` in `.github/workflows/` | “CI never fails” | wave-32 report |
| Security scans | pip-audit / npm audit / semgrep wired as real gates; triage documented | “zero findings forever” | wave-32 |
| MinIO | **BUILT** (wave-31), opt-in | “MinIO not built” | `storage.py`, compose |
| Celery | **BUILT** (wave-31), worker service | “Celery not wired” | `src/backend/workers/` |
| Observability | `/metrics`, `/healthz`, `/readyz`, optional Sentry | Claiming full prod alerting deployed | `docs/OBSERVABILITY.md`, wave-36 |
| Wave-37 | **Review findings pending in parallel** | Invented clean review / fixed CVE list as final | `work/ACTIVE.md`; scratch `_findings-*.md` only |
| Completeness | Product v1.0.1 + quality 32–36/39 shipped; 37/38 close track | “100% complete” | Verdict |
| Deploy | **External blocker** — no IT dept; facts OPEN | “live on client server” | `SEND_IT.md`, SUBMISSION §5B |
