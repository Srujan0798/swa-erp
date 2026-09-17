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
