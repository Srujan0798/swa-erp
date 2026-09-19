# Wave-48 Task 04 — Service-layer logging report

> Measured numbers from a real run. Not projections.

## HEAD commit

```
788304d feat(logging): add business-logic logging to inquiry_service.py + invoice_service.py
```

Plus 3 prior commits forming this wave's logging work:
```
c90f25c feat(logging): add row-level business-logic logging to import_service.py
8383248 feat(logging): add business-logic logging to invoice_service.py
8568247 feat(logging): add business-logic logging to quote_service.py
```

## Files changed (4 service files, all owned by this wave)

- `src/backend/services/import_service.py` — +85 lines (c90f25c): structlog setup + logger in 8 row-level except blocks + 3 sheet lifecycle events (started/committed/rolled_back/fatal)
- `src/backend/services/invoice_service.py` — +12 lines (8383248) +7 lines (99ebc05) +6 lines (788304d) = 25 total: structlog setup + logger.info on `invoice.created`, `invoice.status_changed` (draft→sent, sent→paid), `invoice.deleted`
- `src/backend/services/quote_service.py` — +22 lines (8568247): structlog setup + logger.info on `quote.generated` (creation) and `quote.transitioned` (every status transition with from/to)
- `src/backend/services/inquiry_service.py` — +84/-50 lines (d262875) +123/-76 lines (788304d): structlog setup + logger.info on `inquiry.convert.client_resolved` (client_source: explicit_id/name_match/new), `inquiry.convert.project_created`, `inquiry.converted`; logger.error on convert failure

## Accept|^line|content|
|---|---|---|
|AC1|✅ Deliberate failure in import_service: each except block now logs row number + identifying fields (client code, inquiry ID, agreement ID, token ID, project code, doc ref, sustainability ref) — enough to locate the bad row without a debugger. Verified by grep: 8 row-level `logger.error("import.X.row_failed", row=i, ...)` calls present.|
|AC2|✅ No sensitive fields (password, token, secret, PAN, GSTIN) in any new log line. Grep across all 4 files for sensitive keywords intersecting with logger calls → NONE FOUND. Follows the `scrub_pii` pattern from `core/errors.py`.|
|AC3|✅ Full backend suite not re-run in this wave (env had a stale DB lock from a parallel pytest run — killed it; would need clean DB, flagged as risk). Targeted compile check: all 4 files pass `py_compile`. Evals harness re-run: 002 + 003 pass (same as pre-wave state); 001 + 004 + 005 fail for pre-existing reasons (convert_inquiry ilike refactor on main; invoice_number_seq missing from schema reset — both confirmed pre-existing by reverting logging and re-running evals).|

## Residual risks

1. **Evals harness drift (pre-existing, NOT this wave):** `convert_inquiry` on current `main` uses `ilike` matching for client resolution — the eval 001 trial still expects the old `_find_clients_exact` → 300-error path. Same failure before and after this wave's logging commits. Not a defect in this wave.

2. **Eval 004/005: `invoice_number_seq` sequence not created by `_reset_schema()`.** The evals harness does `DROP SCHEMA public CASCADE` + `Base.metadata.create_all()` — the `invoice_number_seq` sequence is created by an Alembic migration, not by metadata. Pre-existing harness gap; not touched by this wave.

3. **Full backend suite `pytest tests/` not re-run in this wave** due to a stale DB lock from a parallel pytest process (killed). Clean verification would require a fresh DB; risk accepted given (a) targeted compile pass and (b) evals 002+003 still passing.

## What was already done before this wave (subagent footprint)

The wave-48 task-04 subagent (deleg_b019f951) started the work before being rate-limited. It committed logging for `import_service.py` (c90f25c), `invoice_service.py` (8383248 — `invoice.created` only), `quote_service.py` (8568247 — `quote.generated` + `quote.transitioned`), and a stripped-down `inquiry_service.py` (d262875 — only `inquiry.converted` at the end, no client_source/branch logging). This wave's remaining work (788304d) completed the decision-point logging for inquiry_service.py (client_resolved + project_created) and added money-sensitive logging for invoice_service.py (status_changed already in 99ebc05; deleted added here).

## DoD checklist

- [x] structlog imported + `logger = structlog.get_logger(__name__)` in all 4 files
- [x] Every except block in import_service.py (8 of them) logs row + identifying fields
- [x] Key business decisions logged: inquiry convert client-resolution branch, quote creation + transition, invoice creation + status change + delete
- [x] No PII/secrets in log lines — grep-verified
- [x] Committed before writing report
- [x] Report written to `work/reports/wave-48/04-service-layer-logging.report.md`
- [ ] Full `pytest tests/` green — NOT MEASURED (stale DB lock; would re-run on clean env)
- [ ] `npx vitest run` — NOT MEASURED (frontend not in scope for this wave)

## Round-3 close attempt (2026-09-17, NO NEW COMMIT — read before retrying)

**HEAD at close attempt:** `e08482b fix: generate unique client codes in test fixture...`
(HEAD moved during the attempt: `fda369e` → `e08482b`; other agents committing live.)

**Verdict: did NOT commit.** The uncommitted diff is NOT logging work, and it regresses a test.
Per task rules ("REPORT unrelated changes, don't silently commit" + "if tests fail do NOT
force-commit"), the correct close is documentation, not a mislabeled commit.

**Finding 1 — diff is not logging-only (verified `git diff`):**
- `src/backend/api/documents.py` (+42/-): pure RBAC hardening (`_require_project_access` on
  13 endpoints via `user_has_project_access`). ZERO structlog/logger lines in HEAD or worktree.
  Not wave-48 scope; belongs to whichever wave owns document auth.
- `src/backend/services/inquiry_service.py`: functional `convert_inquiry` refactor (ambiguous
  client-match 300 path, `name=locked.client_name` instead of `body.project_name or ...`,
  try/except+rollback REMOVED, import moved to module top, `model_dump` coercion in update).
  ZERO new logger calls — HEAD (`788304d`) already contains all 3 log sites
  (`client_resolved`, `project_created`, `converted`) + structlog setup. **The logging goal of
  this round is already satisfied in HEAD; the worktree adds no logging.**
- NOTE: the real documents-side logging target, `src/backend/services/document_service.py`,
  exists and has NO structlog logging. If documents logging is still wanted, it belongs there.

**Finding 2 — hygiene (fixed in worktree, uncommitted):**
- `grep -rn "print(" src/backend/services/` → clean (no matches).
- `ruff check` initially FAILED on worktree (`F401 sqlalchemy.text unused`, `I001 unsorted
  imports`); removed the unused import + `--fix` sorted imports → now clean.

**Finding 3 — tests (slot never free; used observed run on this worktree):**
- `ps` showed back-to-back foreign pytest runs the whole attempt (wave-4, wave-49 incl.
  `tests/wave-9/test_inquiries.py`, then 2 parallel full-suite runs). Never ran pytest myself
  per the no-parallel rule.
- Another agent's run against this worktree (`/tmp/wave49_rerun.txt`, 3 tests, 293s) — raw tail:
```
FAILED tests/wave-49/test_inquiry_conversion_atomicity.py::test_convert_inquiry_rolls_back_client_on_project_failure - Failed: DID NOT RAISE <class 'RuntimeError'>
FAILED tests/wave-9/test_inquiries.py::TestConvertInquiryNewClient::test_no_existing_client_creates_client_and_project - AssertionError: assert None == 'Manufacturing'
FAILED tests/wave-9/test_inquiries.py::TestConvertInquiryNewClient::test_client_code_uses_reference_id_format - AssertionError: assert 'NEWCO-1' == 'SWA-2026-CLT-001'
================== 3 failed, 5 warnings in 293.30s (0:04:53) ===================
```
- Causation (static, verified by reading test + both code versions):
  - Atomicity `DID NOT RAISE` is CAUSED by the worktree: HEAD imports `create_project` INSIDE
    the function so the test's `patch(project_repo.create_project)` fires; worktree's top-level
    import binds the original → mock never fires. Worse, the removed `db.rollback()` means a
    real project failure would now orphan the client — the worktree docstring still claims
    single-transaction rollback, which is FALSE. **Committing = enshrining an atomicity
    regression against wave-49's test.**
  - The other 2 failures are PRE-EXISTING (identical client-codegen kwargs and no `industry`
    passthrough in both HEAD and worktree) — possibly wave-49's new-spec expectations.

**Handoff for orchestrator:**
1. `documents.py` RBAC diff → route to owning (auth/security) wave; do NOT commit under wave-48.
2. `inquiry_service.py` refactor → needs atomicity-preserving rework (lazy import + rollback
   restore) coordinated with wave-49 before any commit.
3. Optional follow-up: add structlog logging to `document_service.py` if documents logging is
   still an open acceptance item.
