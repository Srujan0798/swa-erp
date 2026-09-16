# Active Work — waves 32-51

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
wave-47 (final seal DoD A-E) ── SHIPPED (2026-08-28)
wave-48 (production hardening) ── SHIPPED (2026-09-15)
wave-49 (transaction atomicity) ── SHIPPED (2026-09-15)
wave-50 (security risks + deterministic tests) ── SHIPPED (2026-09-15)
wave-51 (final re-seal) ── SHIPPED (2026-09-15)
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
| 48 | Production hardening (logging, CSP, pagination, audit, idempotency, frontend loading/bundling) | **SHIPPED** ✅ | 49 | [`work/wave-48/`](wave-48/) | [`work/reports/wave-48/`](reports/wave-48/) |
| 49 | Transaction atomicity for Inquiry→Client→Project | **SHIPPED** ✅ | 40-47 | [`work/wave-49/`](wave-49/) | [`work/wave-49/01-transaction-atomicity.md`](wave-49/01-transaction-atomicity.md) |
| 50 | Security risks (job IDOR, /metrics auth) + deterministic test suite | **SHIPPED** ✅ | 48 | [`work/wave-50/`](wave-50/) | [`work/wave-50/01-deferred-security-risks.md`](wave-50/01-deferred-security-risks.md) |
| 51 | Final re-seal + submission refresh | **SHIPPED** ✅ | 48-50 | [`work/wave-51/`](wave-51/) | [`work/wave-51/01-final-reseal-and-submission.md`](wave-51/01-final-reseal-and-submission.md) |

**Waves 1–39, 43–51 are SHIPPED.** Engineering closed 2026-09-15.

## Status notes (2026-09-15 — HARDENING COMPLETE)

- All professional-grade waves **32–39 SHIPPED**.
- Hardening waves **40–51 SHIPPED**.
- Final close pack: [`work/FINAL-CLOSE/`](FINAL-CLOSE/).
- Seal report: [`work/reports/FINAL-CLOSE.report.md`](reports/FINAL-CLOSE.report.md).
- **External (not engineering):** Viraj server facts / deploy / Excel migration owner.
- **Wave-47 seal:** gates A–E verified 2026-08-28. Backend 572 passed/1 skipped/0 failed;
  85% coverage. Frontend 523 passed/0 failed. See `work/reports/wave-47/01-final-seal.report.md`.
- **Wave-51 re-seal:** commit `93696da`. Backend 63/3/0 (Redis down) / 572/1/0 (Redis up); Frontend 523/0/0; 65.86% coverage.

If a wave is missing from both tables, that is a bug in this file — every wave 1-51 must
appear in exactly one.
