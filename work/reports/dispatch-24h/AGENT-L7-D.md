# AGENT-L7-D

Repo: `/Users/srujansai/Desktop/swa-erp` (main). NO pytest. MAY EDIT: src/backend/api/exports.py, src/backend/workers/tasks.py, src/frontend/src/lib/api.ts, src/frontend/src/pages/ReportsPage.tsx, docs/INSTALL_NO_IT.md, deliverables/MEETING_AND_GO_LIVE_GUIDE.md.

## Decision: UI hook implemented — NOT backend-only doc.

**Backend verified (untouched):**
- Celery workers in `src/backend/workers/tasks.py` — 3 tasks: `generate_project_summary_pdf`, `generate_financial_report_pdf`, `generate_project_slides_pdf`
- `/api/exports/*?async=true` returns `{ job_id }` — 3 endpoints (project summary, financial report, project slides)
- `/api/jobs/{id}` poll with SEC-07 ownership (404-not-403, admin bypass)
- `/api/jobs/{id}/result` returns file download

**Frontend already wired:**
- `src/frontend/src/lib/api.ts` — `startExport`, `getExportJob`, `downloadExportResult`
- `src/frontend/src/pages/ReportsPage.tsx` — "Export summary PDF" button + inline job card (polled 2s, status/error/download link)

## Changes made

**Files added/modified:**
- `src/frontend/src/lib/api.ts` — added `startExport`, `getExportJob`, `downloadExportResult`
- `src/frontend/src/pages/ReportsPage.tsx` — "Export summary PDF" button + inline job card (polled 2s, status/error/download link)

## Verification

- `ruff` PASS
- `black` PASS
- `tsc` PASS
- `eslint` PASS (0 errors/warnings)

## NOT MEASURED

- Redis/celery async export path (environmental, documented)
- Celery worker health on prod (requires live worker + Redis)

## Report

Report written to `work/reports/dispatch-24h/AGENT-L7-D.md`.