# Task 01 — Handover documentation package

## What to do
Build the actual documents Viraj's team will use once this goes live — an admin guide, a
per-role user guide, and a forwardable architecture summary (the specific action item Viraj
requested in Meeting 2 and never got: *"can you share this architecture overview just in text
format... then we can forward it"* — see `resources/MEETINGS_MASTER.md` §Meeting 2 point 11).
None of this depends on Viraj's or IT's still-open answers — it documents what's already built
and verified.

## Files to create
- CREATE: `deliverables/handover/ADMIN_GUIDE.md`
- CREATE: `deliverables/handover/USER_GUIDE.md`
- CREATE: `deliverables/handover/ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md`
- CREATE: `deliverables/handover/TRAINING_ONE_PAGER.md`

(`deliverables/` doesn't exist yet in this repo despite being named in the top-level `CLAUDE.md`
apparatus list — create the directory structure as part of this task.)

## Files you must NOT touch
- Anything under `src/`, `tests/`, `docs/decisions/`, `resources/` — this task only writes new
  deliverable documents, it doesn't change any existing reference material (link to it instead)

## The core problem (inline)

### `ADMIN_GUIDE.md`
For whoever administers the live system day to day. Cover, concretely (not abstractly):
- How to create/manage users and assign roles (the 5 roles: admin, pm, designer, auditor,
  viewer — link to `resources/MEETINGS_MASTER.md` §Meeting 1 §4 for the access-control
  rationale)
- How to run the Excel→ERP import tool (`scripts/import_excel.py`) safely — dry-run first,
  always; link to wave-13's report for the exact usage
- How to run a backup and a restore (link to `docs/runbook_backup_restore.md` — wave-19's
  output; if wave-19 hasn't landed yet when this task runs, note that section as "pending
  wave-19" rather than inventing procedure)
- How to check system health (`/healthz`, docker container status)
- What to do if something looks wrong — a short troubleshooting section covering the most
  likely real issues already documented in this project: dual-Postgres confusion (wave-14's
  report), migration drift symptoms (wave-12/16's reports)

### `USER_GUIDE.md`
Walk through the actual chain a staff member uses day to day, in plain language, one section
per role:
- **PM**: creating an Inquiry, converting it to a Client+Project, creating a Service Agreement,
  issuing Tokens, tracking project status
- **Designer**: working within a Project, creating Document References, logging time
- **Auditor**: compliance checklist review, Reforge/certification document handling
- **Admin**: everything above plus user management (cross-reference the Admin Guide rather than
  duplicating)
- **Viewer**: read-only navigation

Base this on the real chain already built and verified (wave-9's live API smoke test in
`work/reports/wave-12/01-independent-verification.report.md` is a good source for "what actually
works end to end" — don't describe anything that isn't real).

### `ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md`
This is the specific, standalone, forwardable document Viraj asked for — shorter and more
visual than `docs/IT_BRIEF.md` (which goes directly to IT). Base it on `docs/IT_BRIEF.md` Part 3
(the 6 components: backend, frontend, database, file storage, background jobs, auth) plus the
confirmed infra list, but cut the lengthy business-context section — Viraj already knows the
business context, he wants something he can forward *to* IT or keep for his own records. One
screen, plain language, no jargon without a one-line explanation (match the tone already used in
`docs/IT_BRIEF.md` Part 3).

### `TRAINING_ONE_PAGER.md`
A single page: "how to get started" — login URL (placeholder until IT confirms the hostname,
see `docs/DEPLOYMENT_CHECKLIST.md`), first steps per role, where to find the User Guide for
detail, who to contact for access issues.

## Acceptance criteria
- [ ] All 4 documents exist and are internally consistent with each other and with the real,
  verified system behavior (not aspirational features)
- [ ] `ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` is genuinely short enough to forward as-is (target:
  fits on one printed page or one scrollable screen, not another multi-thousand-word brief)
- [ ] No document describes a feature that doesn't actually exist and work — cross-check every
  claim against `plan/EXECUTION.md`'s wave status table before writing it down
- [ ] No document guesses at IT-pending values (hostname, ports) — use the same
  `PENDING IT ANSWER` placeholder convention established in wave-20

## How to deliver
1. Write all 4 documents
2. Cross-check every factual claim against the actual current codebase/reports, not assumption
3. Write report to `work/reports/wave-21/01-handover-documentation.report.md`
4. Stop

## Constraints
- Time budget: 90 min
- Plain language throughout — these are for non-technical staff and the client, not developers
- Allowed tools: file edit, read access to the rest of the repo for fact-checking
