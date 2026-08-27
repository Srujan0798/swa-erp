# Wave 27 — Gotchas

> **Source:** Harvested from `work/reports/wave-27/01-security-findings-and-lint.report.md` — real gotchas only, nothing invented.

## Known pitfalls

### Backup scripts hardened against credential leakage
Backup scripts now hardened against credential leakage. Don't write DB creds to logs or unencrypted files.

### Pre-commit hooks pinned to SHAs
Pre-commit hooks are pinned to specific SHAs (not floating tags). When updating, update the SHA — don't unpin.

### Ruff swept
Ruff debt was swept. Running `ruff check` should be clean. If it's not, fix before merging.

### Backup-safety test suite added
New backup-safety tests verify credential handling. Don't remove them — they catch credential-leak regressions.
