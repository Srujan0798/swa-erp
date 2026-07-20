# Orchestrator Memory

This is the auto-memory index. Entries are appended as the orchestrator learns or makes decisions.

**Updated 2026-07-21** — this file had never been touched since project creation despite 16+
waves shipping since, found by a full-project audit. Populated for real below; keep it current
going forward, don't let it drift again the way `HANDOFF.md`/`plan/EXECUTION.md` did.

## Project state
- **Repo:** swa-erp
- **Created:** May 2026
- **Waves 1-16:** shipped and independently verified (324/324 tests, 7/7 E2E)
- **Waves 17-21:** production-readiness/handover, check `work/reports/wave-N/` for landed status
- **Waves 22-25:** security/correctness/dead-code/UI-wiring fixes from a 2026-07-21 four-agent
  full-project audit — check `plan/EXECUTION.md`'s status table for current state
- **External blockers:** Viraj's 3 open decisions (`docs/decisions/0002-core-id-chain-gap.md`),
  IT's 8 infra answers (`docs/IT_BRIEF.md`, sent, awaiting reply)
- **OS-Setup version:** v1.1

## Session decisions (most recent first)
- 2026-07-21: found and fixed a 3-way contradiction across `HANDOFF.md` and `plan/EXECUTION.md`
  on "what wave are we on" — a leftover section from wave-3 was never updated across 13
  subsequent waves. Lesson: status-tracking docs need their OLD sections actively removed when
  superseded, not just new sections appended on top.
- 2026-07-21: `plan/ARCHITECTURE.md` and `orchestrator/rules/security.md` both described
  features as implemented (RS256 JWT, Sentry, Prometheus, HTTPS-only cookies, refresh-token
  rotation, CI security gates that block) that were never actually built. Lesson: any doc
  claiming "X is integrated/implemented" needs a grep-verified citation, not just a plan
  restated as fact after time passes.

## Patterns learned
- This test suite (`tests/`) produces false mass-failures under process/DB contention (stray
  pytest processes racing on `DROP SCHEMA public CASCADE` against the shared local
  `swa_erp_test` Postgres) — always confirm no other pytest process is running and consider a
  fresh `DROP DATABASE`/`CREATE DATABASE` before trusting a failure count from this suite. See
  `docs/PROJECT_HISTORY.md` for the original ENUM/fixture-scoping version of this same class of
  bug.
- Systemic bug pattern across several modules: "create/delete" endpoints are reliably role-
  gated, but the workflow-transition endpoints next to them (task transitions, RFQ send/respond/
  close, invoice status change) are frequently left at "just logged in" — check transition
  endpoints specifically when auditing RBAC, not just CRUD.
- Systemic pattern: multiple models have a `deleted_at` column that's either never used (dead
  soft-delete column) or paired with a function named `soft_delete()` that actually hard-deletes
  — don't trust a column's existence as proof soft-delete works, verify the actual delete path.

## Recurring blockers
- None currently blocking code work. Two external blockers exist (Viraj's answers, IT's
  answers) but both are isolated so they don't block anything else — see Project state above.

## Verified facts about the codebase
- Auth: JWT HS256 only (no RS256), Bearer token in Authorization header, both access + refresh
  tokens stored in frontend `localStorage` (not cookies), refresh does not rotate.
- Money: `Decimal(18,2)` convention followed almost everywhere; one confirmed violation in
  `lifecycle.py`'s `ProjectStatsResponse.total_estimated_value` (float cast) — see wave-23.
  GST is not implemented on invoices (generic tax_rate/tax_amount only) — see wave-18.
  `Project` model has no `version` column despite being cited as having optimistic locking.
- Reference-ID scheme: `SWA-{year}-{TYPE}-{seq:03d}`, atomic via
  `src/backend/services/reference_id_service.py`, confirmed race-safe under concurrency testing.
- Real runtime storage is a flat `uploads/<id>/` directory at repo root (gitignored) — not
  `data/`, not MinIO, despite some docs describing those as already built.
