# Wave 28 — Gotchas

> **Source:** Harvested from `work/reports/wave-28/01-execute-doc-consolidation.report.md` — real gotchas only, nothing invented.

## Known pitfalls

### HANDOFF_FINAL.md / wave9handoff.md / wave10handoff.md archived via git mv
These files were archived (not deleted) via `git mv`. Old references to them in handoffs/docs are now stale.

### KIMI.md → CLAUDE.md symlink
KIMI.md is now a symlink to CLAUDE.md. Byte-identical alias is a maintenance trap — one edit silently diverges; a symlink preserves the "interchangeable orchestrator" behavior with zero drift risk.

### ADR-0003 de-duplicated
ADR-0003 was de-duplicated. If you see duplicate ADR content, it's stale.

### Conventions/history enriched
`docs/conventions.md` and `docs/historical/` were enriched. Check them before writing new conventions docs — don't duplicate.
