# Active Work — waves 32-39

Live wave tracking. Waves 1-31 (shipped history) live in
[`work/ARCHIVE.md`](ARCHIVE.md). Every wave appears in exactly one of the two files.

## Dependency order

```
wave-32 … 36, 39 ── SHIPPED
wave-37 (independent review) ── SHIPPED (final close 2026-08-23)
wave-38 (submission package) ── SHIPPED (final close 2026-08-23)
wave-43 (evals scaffold) ── SHIPPED (worktree, report at work/reports/wave-43/01-evals.report.md)
wave-44 (metrics hardening) ── SHIPPED (worktree)
wave-45 (skill schema 2.1) ── SHIPPED (worktree)
wave-46 (FINAL-CLOSE rewrite) ── SHIPPED (worktree, work/reports/wave-46/)
wave-47 (final seal DoD A-E) ── SHIPPED (THIS WAVE)
```

## Wave table

| # | Purpose | Status | Depends on | Brief | Report |
|---|---|---|---|---|---|
| 32 | Make CI real (remove fake gates) + security scanning | **SHIPPED** ✅ | — | [`work/wave-32/`](wave-32/) | [`work/reports/wave-32/`](reports/wave-32/) |
| 33 | Close backend coverage gaps (82% → ≥85%) | **SHIPPED** ✅ | 32 | [`work/wave-33/`](wave-33/) | [`work/reports/wave-33/`](reports/wave-33/) |
| 34 | Build a real frontend test suite (≥60% coverage) | **SHIPPED** ✅ | 32 | [`work/wave-34/`](wave-34/) | [`work/reports/wave-34/`](reports/wave-34/) |
| 35 | Load-test validation (10/50/100/150 users) | **SHIPPED** ✅ | 32 | [`work/wave-35/`](wave-35/) | [`work/reports/wave-35/`](reports/wave-35/) |
| 36 | Production observability (metrics + error tracking) | **SHIPPED** ✅ | 32, best after 35 | [`work/wave-36/`](wave-36/) | [`work/reports/wave-36/02-post-merge-fixes.report.md`](reports/wave-36/02-post-merge-fixes.report.md) (01 never written) |
| 37 | Independent adversarial review (multi-agent) | **SHIPPED** ✅ | 32, 33, 34, 35 | [`work/wave-37/`](wave-37/) | [`work/reports/wave-37/01-independent-review.report.md`](reports/wave-37/01-independent-review.report.md) |
| 38 | Professional submission package | **SHIPPED** ✅ | 32-37 | [`work/wave-38/`](wave-38/) | [`work/reports/wave-38/01-submission-package.report.md`](reports/wave-38/01-submission-package.report.md) |
| 39 | Repo organization | **SHIPPED** ✅ | 1/1 | [`work/wave-39/`](wave-39/) | [`work/reports/wave-39/`](reports/wave-39/) |
| 40-47 | Final seal passes (skill schema, metrics hardening, FINAL-CLOSE rewrite, evals, DoD A–E) | **SHIPPED** ✅ | — | worktrees `w44`/`w45`/`w46`/`w47` | [`work/reports/wave-47/01-final-seal.report.md`](reports/wave-47/) |

**Waves 1–39, 43–47 are SHIPPED.** Engineering closed 2026-08-28.

## Status notes (2026-08-23 — ENGINEERING CLOSED)

- All professional-grade waves **32–39 SHIPPED**.
- Final close pack: [`work/FINAL-CLOSE/`](FINAL-CLOSE/).
- Seal report: [`work/reports/FINAL-CLOSE.report.md`](reports/FINAL-CLOSE.report.md).
- **External (not engineering):** Viraj server facts / deploy / Excel migration owner.
- **Wave-47 seal:** gates A–E verified 2026-08-28. Backend 572 passed/1 skipped/0 failed;
  85% coverage. Frontend 523 passed/0 failed. See `work/reports/wave-47/01-final-seal.report.md`.

If a wave is missing from both tables, that is a bug in this file — every wave 1-39 must
appear in exactly one.
