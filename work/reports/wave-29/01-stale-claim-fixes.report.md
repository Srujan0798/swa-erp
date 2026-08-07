# Task 01 — Fix the remaining stale claims across current docs

## Result
**DONE** — all 9 items fixed and each verified against the real repo. Docs-only changes; the
full pytest suite still passes 393/393 and pre-commit preflight passes. Committed as `39a6c12`.

## Per-item: what it said → what it says now → how verified

### 1. `docs/runbook.md` — wave-19 "not built yet" backup section
- **Said:** wave-19 backup scripts don't exist; backups are manual only.
- **Now:** points at `docs/runbook_backup_restore.md`; lists `make backup-db` /
  `make backup-files` / `make restore-db` and the wave-19 + wave-27 test suites.
- **Verified:** `ls scripts/` → `backup_db.sh backup_files.sh restore_db.sh` (all `-rwxr-xr-x`);
  `work/reports/wave-19/01-backup-and-ops-scripts.report.md` exists (DONE, live round-trip);
  `git show aa60e73 --stat` shows wave-27 hardened `backup_db.sh`/`restore_db.sh` + added
  `tests/wave-27/test_backup_script_safety.py`.

### 2. `deliverables/handover/ADMIN_GUIDE.md` — same wave-19 "PENDING WAVE-19" block (client-facing)
- **Said:** backup/restore runbook "has not been built yet", "no automated backup procedure
  shipped in this repo".
- **Now:** plain-language corrected block: `make backup-db`, `make backup-files`,
  `make restore-db file=<path>`, cron pointers, retention defaults flagged as non-confirmed,
  and the two test files as evidence.
- **Verified:** same evidence as #1; doc is in `deliverables/handover/` (client-facing) so
  wording is plain and accurate.

### 3. `docs/conventions.md` — GST "not implemented" + error-shape `{detail, code, request_id}`
- **Said:** GST not implemented (no `gst_amount`, no HSN/SAC, no GSTIN); errors are always
  `{detail, code, request_id}`.
- **Now:** GST is implemented at invoice level (wave-18, `2073c36`, migration `0025`):
  `gst_percent` + `gst_amount` computed in `invoice_service.py`; honestly notes what is NOT
  GST-specific yet (no HSN/SAC, no GSTIN). Error shape corrected: body is `{"detail": "..."}`
  (standard FastAPI `HTTPException`), `X-Request-ID` is a header only; no `code`/`request_id`
  in the body.
- **Verified:** `grep -n "gst" src/backend/models/invoice.py src/backend/schemas/invoice.py`
  → `gst_percent`/`gst_amount` present; `src/backend/services/invoice_service.py:25-28`
  computes them; `git show 2073c36` shows migration `0025_add_invoice_gst.py`. For errors:
  `grep exception_handler src/backend/main.py` → none; `src/backend/core/middleware.py` sets
  `X-Request-ID` header only; API routers raise `HTTPException(status_code=..., detail=...)`.

### 4. `orchestrator/memory/MEMORY.md` — test count "324/324" + GST "not implemented"
- **Said:** "Waves 1-16 ... (324/324 tests...)"; "GST is not implemented on invoices".
- **Now:** "Test suite: **393/393 passing** (verified 2026-08-07)"; GST implemented (wave-18),
  with the same HSN/SAC/GSTIN caveat.
- **Verified:** live `python3 -m pytest tests/ -q` → **393 passed**; model/migration evidence as
  in #3.

### 5. `HANDOFF.md` — test count "324/324 backend tests"
- **Said:** "Waves 1-16 ✅ SHIPPED and independently verified (324/324 backend tests, 7/7 E2E...)".
- **Now:** removed the stale count from the wave-1-16 sentence and added "Backend test suite:
  393/393 passing (verified 2026-08-07)" with a correction note.
- **Verified:** live `pytest tests/ -q` → 393 passed.

### 6. `plan/ARCHITECTURE.md` — Celery in diagram without target-vs-real marking
- **Said:** diagram showed `Redis (Celery + cache)` and a `Celery (workers)` box as live, plus
  "queued via Celery"/"Celery + Redis broker" rows in the Integrations table.
- **Now:** diagram has a truth note, `Redis (cache only today)`, `Local FS (uploads/ at repo
  root)`, and the Celery box is tagged `[TARGET] — installed but unimplemented`. The
  Integrations table and the "Celery worker crashes" failure row are marked TARGET / N/A today.
- **Verified:** `grep -rn "celery\|@task\|Celery(" src/backend --include="*.py"` → zero matches
  (only `requirements.txt: celery==5.4.0`).

### 7. `README.md` — Celery/MinIO wording implied both live
- **Said:** "Backend: ... Celery · Redis", "Storage: Local filesystem (dev) → MinIO/S3 (prod)".
- **Now:** backend lists Redis only, storage is "Local filesystem only — `uploads/` at repo
  root", plus a corrected note: "Celery and MinIO are NOT live... both remain target-state".
- **Verified:** `grep -rn celery src/backend` → no code; `grep -rn minio src/backend` → no code.

### 8. `resources/EXCEL_SHEETS_INVENTORY.md` — Status column
- **Said:** Time Logging (Wave-7), Sustainability (Wave-8), Document Reference (Wave-6) rows
  marked `⏳ Pending`; "Next Steps: Complete Waves 4-8" and "Wave-4 ... READY TO DISPATCH".
- **Now:** Status column values changed to `✅ Shipped` for those rows (Wave column mapping and
  entity mapping untouched, per brief); Wave-4 heading → `(SHIPPED)` with a correction note that
  waves 4-8 shipped and the section is historical planning text.
- **Verified:** `plan/EXECUTION.md` status table lists waves 4-8 as **SHIPPED**; models exist:
  `src/backend/models/{time_tracking,sustainability_metric,document_reference}.py`.

### 9. `CHANGELOG.md` — version vs git tags inconsistent
- **Said:** `## [0.3.0] — 2026-07-20` as a normal release, with compare links to `v0.1.0`/
  `v0.2.0`/`v0.3.0` tags.
- **Now:** top correction note stating the real tag state (`git tag -l` → only
  `wave-3-complete`; no `v0.1.0`/`v0.3.0`), version files still `0.2.0`, the `[0.3.0]` entry was
  never cut as a release, and wave-30 will cut `1.0.0` and fix the link refs. Heading changed to
  "`[0.3.0]` — 2026-07-20 (never released — no tag; version files still 0.2.0)".
- **Verified:** `git tag -l` → `wave-3-complete`; `grep version pyproject.toml` → `0.2.0`;
  `grep '"version"' src/frontend/package.json` → `0.2.0`; `work/reports/wave-30/` empty (wave-30
  not run yet), so noted the current version honestly rather than inventing `1.0.0`.

## Acceptance criteria check

- [x] All 9 items corrected, each verified against the real repo (evidence above)
- [x] `grep -rn "Celery" --include="*.md" . | grep -v historical | grep -v attic` — every
      remaining mention in living docs is now explicitly marked as target-state/not-implemented
      or sits in a decision/meeting record framed as a target decision (`MEETINGS_MASTER`,
      `docs/decisions/*`) — see note below
- [x] Same for `MinIO` — `docs/runbook_backup_restore.md:18` is conditional ("If/when MinIO or
      S3 is wired in"); handover `ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` already said "planned but
      not built yet"; ADR-0003 and MEETINGS_MASTER now carry target-decision notes
- [x] No current doc states a test count that disagrees with a live run — all current count
      claims now say 393/393 (MEMORY.md, HANDOFF.md); `plan/EXECUTION.md`'s 52/97/324 figures are
      per-wave historical records tied to specific commits, not current-state claims
- [x] `deliverables/handover/*` — zero claims about unbuilt features; ADMIN_GUIDE §3 rewritten,
      ARCHITECTURE_OVERVIEW already honest, USER_GUIDE/TRAINING_ONE_PAGER contain no such claims
      (grep for celery/minio/s3/rs256/sentry/prometheus/queued/worker → no matches)
- [x] `python3 -m pytest tests/ -q` → **393 passed, 42 warnings** (two runs, both 393)
- [x] Pre-commit preflight passes (`trim trailing whitespace`, `fix end of files`,
      `check for added large files`, `detect private key`, `OS-Setup Preflight`, `Block
      accidental secret commits` all Passed; ruff/black/yaml/json/toml had no matching files)

## Judgment call (items 6-7 grep sweep)
The brief's fix list covered 9 docs, but the acceptance greps surfaced Celery/MinIO mentions in
a few more **living** docs. I applied the same "mark or delete" rule to them rather than leaving
unmarked claims: `CLAUDE.md` (tech stack + storage lines), `HANDOFF.md` (tech-stack line),
`plan/PRD.md` (R6 storage + frozen-stack constraint), `docs/IT_BRIEF.md` (Part 3 target
architecture), `docs/decisions/0001-tech-stack.md` ("Used in wave-3+ for PDF gen, email send" —
a factual claim, now corrected to "never implemented"), `docs/decisions/0003-it-server-call-brief.md`
(target-decision notes), and `resources/MEETINGS_MASTER.md` (note that "Confirmed" = confirmed
target decisions, not built). These are all small inline text notes; no restructuring. The
remaining bare mentions in `MEETINGS_MASTER` (proposal diagram) and `docs/decisions/0003` are
framed as meeting/decision records and are now covered by the added target-state notes.

## Files NOT touched (per brief)
- No source code, tests, migrations, or compose files (docs-only task).
- No documents moved or restructured.

## Blockers
None.
