---
name: audit
description: Deep audit of a wave or module. Usage /audit wave-N or /audit module=auth
---

# /audit

## What this does
Independent deep review — not just acceptance pass/fail, but architecture + style + security + tests + docs.

## Audit checks (per module)
- Architecture: matches `plan/ARCHITECTURE.md`?
- Style: matches `orchestrator/rules/`?
- Security: SQL injection, XSS, secret exposure, missing auth?
- Tests: coverage ≥ target? edge cases? flakiness?
- Docs: API documented? ADR for non-obvious decisions?
- Performance: hits budgets in PRD?
- Constitution compliance: every principle respected?

## Output
Audit report at `docs/audits/wave-N-audit-{date}.md` with findings:
- CRITICAL (must fix before next wave)
- HIGH (fix in next wave)
- MEDIUM (track in backlog)
- LOW (nice to have)
