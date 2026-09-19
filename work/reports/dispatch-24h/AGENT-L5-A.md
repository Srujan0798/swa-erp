# AGENT-L5-A

Repo: `/Users/srujansai/Desktop/swa-erp` (main). Core-sheet import dry-run — **fresh paste**. No commit, DB untouched (dry-run rolls back each sheet).

## Command

`/usr/local/bin/python3.11 scripts/import_real_sheets.py` (default = dry-run, no `--commit`)

## Dry-run row counts (2026-09-19)

```
OK  inquiries              total=  3 created=  0 updated=  3 skipped=  0 errors=0
OK  clients                total=  3 created=  0 updated=  3 skipped=  0 errors=0
OK  agreements             total=  3 created=  0 updated=  3 skipped=  0 errors=0
OK  projects               total=  0 created=  0 updated=  0 skipped=  0 errors=0
```

All 4 core sheets import cleanly: 9 real rows total, **0 errors**. "updated" (not "created") because these rows were already committed to the dev DB in an earlier session and the import is idempotent by reference ID.

## Notes

- **First Lead ID / LDI ignored** — verified in code: `_is_legacy_lead_ref()` (import_service.py:156-158) drops any `LDI-`/`-LDI-` reference; inquiries skip counter would tick if present in the sheet.
- **Projects sheet empty** — `projects total= 0` confirms the client's Project Tracking sample is empty. Projects in the product come from **Inquiry → Convert** (verified in L3-A report and wave contracts). The dev DB's projects (CON/DBR/CAS/GAD chain) were created by convert + `make swa-live-local`, not by a faked tracking import.
- **Downstream sheets not imported** — tokens, document_references, time_logs, sustainability are intentionally omitted from `bootstrap_real.py` ORDER. They require projects created by Convert (Meeting 2 rule). The meeting demo will: import base sheets → live convert → then create tokens/docrefs/time/sustainability.

## NOT MEASURED

- `--commit` run against a fresh DB (would show created=9); NOT done — do not re-import/pollute before the meeting.

## Verification (worktree-based, not merged to main)

- Work performed in isolated worktree; changes not merged to `main` branch
- No live server verification performed (worktree not deployed)
- Static checks (ruff, black, eslint, tsc) — **NOT RUN** in this session
- Test suite execution — **NOT RUN** in this session
- Evidence for implementation: see corresponding worktree or main branch history
- **Status: SUMMARY ONLY** — detailed verification deferred to merge-time review
