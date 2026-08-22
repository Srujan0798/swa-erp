# Handoff Protocol

> **Role:** Session / orchestrator-switching protocol. Part of the front-door set — start at
> [README.md](README.md).

## Why this file exists
Switching orchestrators or starting a fresh session shouldn't require re-explaining the project.
This file lets the new session catch up in < 5 minutes.

## Current state (2026-08-23 — FINAL CLOSE IN PROGRESS)

- **Product:** **v1.0.1** feature-complete (waves 1–31). Core chain, Excel import, MinIO opt-in,
  Celery workers — shipped earlier.
- **Professional-grade track (waves 32–39):**
  - **SHIPPED:** 32 (real CI), 33 (backend 86% cov), 34 (frontend ≥60%), 35 (load tests),
    36 (metrics/Sentry/readyz — task-01 report missing, 02+code landed), 39 (repo org).
  - **IN-FLIGHT:** **37** independent adversarial review.
  - **QUEUED:** **38** submission package (after 37).
- **HEAD baseline when close started:** `4b8ba31` (+ stabilize commits landing now).
- **Close pack (authoritative):** [`work/FINAL-CLOSE/`](work/FINAL-CLOSE/) — protocols P01–P20,
  paste prompts, definition of done.
- **Living verdict:** [`work/reports/COMPLETION-HANDOFF-VERDICT.md`](work/reports/COMPLETION-HANDOFF-VERDICT.md)
- **Live wave table:** [`work/ACTIVE.md`](work/ACTIVE.md) (not this file’s Aug-11 freeze).

### Stabilize fixes in the close
- TaskCard overdue test: local Y-M-D dates (not `toISOString` UTC).
- CI: `npx vitest run` in frontend job.
- Viraj architecture overview: MinIO/Celery status corrected.
- `task_repo` priority maps consolidated to one `_PRIORITY_MAP`.
- Note: live unauthenticated responses are **401** in this stack; do not “fix” tests to 403 without re-measuring.

### Client / deploy (external — does not block engineering close)
- Viraj data Qs **answered** (ADR-0002). Lead ID columns removed.
- **No IT department** — server facts slow path; use `docs/INSTALL_NO_IT.md` when he has time.
- Do **not** re-blast `SEND_IT.md` / `SEND_VIRAJ.md`.

### Where to start a new session
1. This file
2. `work/FINAL-CLOSE/README.md` if closing
3. `work/ACTIVE.md` for wave status
4. `Claude.md` kernel

## When you've just merged a wave
Update `work/ACTIVE.md` (SoT) and this file’s “Current state” bullet.

## Open decisions (live)
- Server/deploy 8 facts — Viraj / nominee (external)
- Excel migration owner + freeze date — Viraj (external)

## Wave roadmap recap
1–31 product MVP → v1.0.1 ✅  
32–36 + 39 professional evidence ✅  
37 review → 38 package → seal (this close)
