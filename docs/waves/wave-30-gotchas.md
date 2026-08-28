# Wave 30 — Gotchas

> **Source:** Harvested from `work/reports/wave-30/01-final-release-and-submission.report.md` — real gotchas only, nothing invented.

## Known pitfalls

### Full verification sweep performed
Wave-30 did a full verification sweep + live end-to-end business-flow validation. Version cut at 1.0.0, `deliverables/SUBMISSION.md` produced.

### Version cut at 1.0.0
The release was cut at 1.0.0. But `pyproject.toml` and `package.json` may still reflect older versions — check current state.

### Submit package produced
`deliverables/SUBMISSION.md` produced. If you need the submission package, it's there — don't rebuild it.

### Engineering sealed in FINAL-CLOSE
Engineering sealed in `work/reports/FINAL-CLOSE.report.md`. Waves 32-39 SHIPPED. Product release remains v1.0.1.
