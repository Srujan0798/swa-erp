# Changelog

All notable changes to this project will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Corrected 2026-08-07** — release-versioning reconciliation against real git state
> (`git tag -l`). Only one tag exists: `wave-3-complete` (points at the v0.2.0 bump commit
> `3a66b7a`). There is **no `v0.1.0` and no `v0.3.0` tag**, and the version files
> (`pyproject.toml`, `src/frontend/package.json`) still say `0.2.0`. The `[0.3.0]` entry below
> describes work that was merged to git but **never cut as a release** — the compare links used
> to point at tags that don't exist. The first real release will be `1.0.0`, cut by wave-30
> (see `work/wave-30/01-final-release-and-submission.md`); this changelog will get its
> `[1.0.0]` entry and the link refs fixed there.

## [0.3.0] — 2026-07-20 (never released — no tag; version files still 0.2.0)
### Added
- Wave-9: the actual client-requested core chain — Inquiry, Service Agreement, Token,
  Document Reference (`SWA-{year}-{TYPE}-{seq}` shared reference-ID generator), frontend for
  the full chain. Closes the gap documented in `docs/decisions/0002-core-id-chain-gap.md`
  (waves 1-8 had built a generic CRM, not this).
- Wave-10: Sustainability metrics (project-level, post-completion)
- Wave-13: Excel → ERP one-time migration importer (dry-run by default, idempotent)
- Wave-14: Docker Compose auto-migration on boot; fixed backend image missing `scripts/`
- `resources/MEETINGS_MASTER.md` — consolidated, corrected record of both client meetings
- `docs/decisions/0001` through `0004` (ADRs: tech stack, core ID-chain gap, IT server brief,
  meeting-2 flow/next-steps)
- `docs/PROJECT_HISTORY.md` — distilled replacement for the 142-session `ULTIMATE_HANDOFF.md`
- `docs/IT_BRIEF.md` — full deployment brief for the client's IT/server admin

### Fixed
- Wave-11: reconciled 8 modified + 8 untracked dangling frontend files from prior sessions
- Wave-12 (independent verification): fixed a broken Alembic migration chain (3 wrong
  `down_revision` pointers), a missing `email-validator` dependency that crashed the backend
  Docker image at import time, model/migration drift on `Task` and `Document` (columns the
  ORM models had that their migrations never created — caused live 500s), and added the
  missing `nginx.conf` for the frontend container's SPA routing. Full backend suite
  independently re-verified at 324/324 passing.

### Changed
- Corrected `docs/SCOPE_GUARD.md` and `orchestrator/core/scope-guard.md`: MVP was
  incorrectly framed as "waves 1-4"; the real MVP boundary is waves 1-13 once the core chain
  (wave-9) is counted.

### Archived (not deleted — see `docs/historical/`)
- `handoffs/` (142 files), `merged_handoffs/` (35 files), `session_exports/` (142 raw session
  logs), `ULTIMATE_HANDOFF.md`, `FINAL_SPEC.md` (materially stale — claimed waves 3-8
  uncommitted and Docker unverified, both long since resolved), original meeting transcripts
  and their "clean" summaries (superseded by `resources/MEETINGS_MASTER.md`)

## [0.2.0] — 2026-07-03
### Added
- Wave-3: Quotation / BOQ Workflow — BOQ upload (JSON/Excel), versioning, quote generation, PDF export, frontend UI
- Wave-3 acceptance tests: 5/5 passing

## [Unreleased]
### Added
- Initial project structure generated from OS-Setup v1.1
- Strategy docs: PRD, ARCHITECTURE, EXECUTION
- Constitution + wave-1 spec/plan/tasks/contracts
- Orchestrator apparatus: 10 commands, 12 skills, 5 sub-agents, 7 hooks, 2 recipes, 4 rule sets
- Wave-1 task briefs ready to dispatch
- Documentation: SCOPE_GUARD, conventions, runbook, conflict_resolution, api, deployment, ADR-0001

## [0.0.0] — 2026-05-19
### Added
- Repository initialized.

[0.3.0]: ../../compare/v0.2.0...v0.3.0
[0.2.0]: ../../compare/v0.1.0...v0.2.0
[Unreleased]: ../../compare/v0.3.0...HEAD
