# Changelog

All notable changes to this project will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Reconciled 2026-08-07 by wave-30** — the first real release, **v1.0.0**, was cut today
> (tag `v1.0.0`, version files `pyproject.toml` / `package.json` / `package-lock.json` all set
> to `1.0.0`). The only prior git tag is `wave-3-complete` (the old `0.2.0` bump commit
> `3a66b7a`); there is **no `v0.1.0` and no `v0.3.0` tag**, so the `[0.3.0]` entry below
> (describing waves 9-21, merged but never cut) has no git compare range of its own. The
> `[1.0.0]` entry compares against `wave-3-complete`, which is the last real tag.

## [1.0.1] — 2026-08-10 — deferred-feature release (wave-31)

Wave-31 closed the two last deferred features from `SUBMISSION.md` §3/§9: object storage and
background jobs. No breaking changes — the default `local` storage backend and the synchronous
export path are byte-identical to 1.0.0.

### Added
- Wave-31 task 01 (object storage, `d5dd6f1`): `StorageBackend` abstraction
  (`src/backend/core/storage.py`) with a `local` backend (default — `uploads/`, byte-identical
  to 1.0.0) and an opt-in `minio` backend (`STORAGE_BACKEND=minio`); new `minio` compose service.
  Document/BOQ/signed-PDF file writes now route through `get_storage()`.
- Wave-31 task 02 (Celery worker, `9d9f80e`): a real Celery app (`src/backend/workers/`) with
  `celery_app` and `@task`s for background PDF/report generation, a `worker` compose service
  (Redis as broker/backend), async export endpoints (`?async=true` → `202` + `job_id`, poll
  `GET /api/jobs/{id}`), and a job-status/result router. The synchronous export path is unchanged.
- Wave-31 tests: `tests/wave-31/test_celery_tasks.py` (7 tests, eager mode).

### Fixed
- Wave-31: `docs/runbook.md`, `HIERARCHY.md`, `README.md`, and `docs/conventions.md` updated to
  reflect the live storage and Celery implementation (previously documented as target-state).

### Changed
- Version cut `1.0.0` → `1.0.1` in `pyproject.toml`, `src/frontend/package.json`,
  `package-lock.json` (wave-31 features landed after the `v1.0.0` tag, so they ship in this patch
  release rather than retroactively in 1.0.0).
- Alembic migration graph collapsed from 7 heads to 1 (commit `c4dd496`, follow-up to
  `SUBMISSION.md` §4.4 / §9).

## [1.0.0] — 2026-08-07 — client submission release

First release. Covers everything since `wave-3-complete` (waves 22-30), plus the cumulative
state of waves 1-21. Reference-ID convention across the system: `SWA-{year}-{TYPE}-{seq:03d}`.

### Added
- Wave-22 (RBAC/auth hardening): materials read endpoints now require authentication; financial
  modules (`project_pnl`, `exports`, invoice-status) are role-gated; core-chain access matrix now
  matches the client's matrix (PM+Designer create DBR/KDR, Auditor+Designer create Reforge);
  compliance-item review accepts Auditor+Designer; task transitions/reorder/comment/bulk-status
  and RFQ send/respond/compare/close/cancel are PM-gated.
- Wave-23 (correctness): optimistic-locking `projects.version` column (migration 0027) with
  409-on-stale-update; real soft-delete on `Task` (row survives, hidden from list/get/count).
- Wave-24 (UI wiring): Notifications bell + mark-read; New User dialog, delete-user and
  delete-client UI; Tokens nested under agreements and a Document References tab on project
  detail (both previously unreachable); dead debug endpoint and dead board page removed.
- Wave-27 (security): hardened backup/restore scripts against credential leakage; pre-commit
  hooks pinned to SHAs; backup-script safety test suite.
- Wave-30 (release): `deliverables/SUBMISSION.md` — the client submission package (what was
  built, verification evidence, drop list, known limitations, blockers, deploy + import
  pointers, docs map, next steps).

### Fixed
- Wave-22: invoice-status mutation was unauthenticated-in-effect (now PM); task/RFQ transition
  endpoints had zero role gate (now PM).
- Wave-23: financial report PDF fabricated 70/30 ratios (now computed from real `ProjectCost`
  rows + billable hours at the shared `DEFAULT_HOURLY_RATE`); `total_estimated_value` was a
  lossy `float` (now `Decimal`).
- Wave-24: `New User` button previously did nothing (mutation object discarded); notifications
  endpoints returned stubs; `api.deleteClient` frontend method was missing.
- Wave-27: backup scripts could print the DB password on stderr.
- Wave-29: nine docs carried stale claims (backups, GST, Celery/MinIO target-state, test counts,
  version/tag reality) — all corrected against the real repo.
- Wave-30: Alembic cold boot could fail because migration `0026` dropped a `documents` column
  before the sibling branch created the table — `0026` now declares `depends_on = "0022"`;
  FastAPI `Notification` type import was missing in the frontend API client (resolved to the DOM
  global — TS errors); remaining `B008` FastAPI-DI patterns got inline `# noqa` (wave-27
  convention); dev compose now allows disabling the auth rate limiter so the e2e suite (7 logins
  in under a minute) is not throttled.

### Changed
- Version cut from `0.2.0` → `1.0.0` in `pyproject.toml`, `src/frontend/package.json`, and
  `package-lock.json` (first real release; `0.3.0` was never cut as a tag).
- Wave-28: docs consolidated — `HANDOFF_FINAL.md`/`wave9handoff`/`wave10handoff`/`OS_SETUP.md`
  archived via `git mv` to `docs/historical/` and `attic/`; `KIMI.md` is now a symlink to
  `CLAUDE.md`; ADR-0003 de-duplicated to a pointer at `docs/IT_BRIEF.md`.
- Wave-26: 142 session handoffs merged → distilled into `docs/PROJECT_HISTORY.md`; 122 MB of
  raw session exports triaged (no secrets found) and left archived.

### Security
- Wave-22: closes the unauthenticated-materials and zero-RBAC-on-financial-modules findings from
  the 2026-07-21 four-agent audit.
- Wave-27: credentials no longer leakable from `scripts/backup_db.sh` / `scripts/restore_db.sh`;
  third-party pre-commit hooks pinned to immutable SHAs.
- Auth remains JWT HS256 over HTTPS with RBAC and an IP-based auth rate limiter
  (default 5 login/min; `DISABLE_AUTH_RATE_LIMIT=true` for test/dev).

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

## [0.0.0] — 2026-05-19
### Added
- Repository initialized.

[1.0.0]: ../../compare/wave-3-complete...v1.0.0
[1.0.1]: ../../compare/v1.0.0...v1.0.1
