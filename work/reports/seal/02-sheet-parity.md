# Sheet parity matrix — director cutover

**Source inventory:** `resources/EXCEL_SHEETS_INVENTORY.md`  
**Status:** scaffold this seal session — agent must fill Screen/API/GAP against live app.  
**Production path:** `make swa-live-local` + `resources/ERP Sheets` (NOT `make seed-demo`).

| # | Sheet | Client still edits columns | Replaces in ERP (screen) | API | Importer | GAP / data lost on cutover | Status |
|---|-------|---------------------------|---------------------------|-----|----------|----------------------------|--------|
| 1 | Clients Sheet.xlsx | name, contact, … | Clients list/detail | `/api/clients` | import-data dry-run | TBD | OPEN |
| 2 | Inquiries Sheet.xlsx | lead fields | Inquiries | `/api/inquiries` | TBD | TBD | OPEN |
| 3 | Service Agreements Sheet.xlsx | agreement terms | Agreements | `/api/agreements` | TBD | TBD | OPEN |
| 4 | Tokens Sheet.xlsx | token burn | Tokens | `/api/tokens` | TBD | TBD | OPEN |
| 5 | Document Reference Sheet.xlsx | DRN meta | Document References | `/api/document_references` | TBD | TBD | OPEN |
| 6 | Project Tracking Sheet.xlsx | status, milestones | Projects | `/api/projects` | TBD | TBD | OPEN |
| 7 | Time Logging Sheet.xlsx | hours, billable | Time tracking | `/api/time_tracking` | TBD | TBD | OPEN |
| 8 | Sustainability Metrics Sheet.xlsx | green metrics | Sustainability | `/api/sustainability_metrics` | TBD | TBD | OPEN |

**Drop from MVP (Meeting 2):** Admin process, complaints, feedback, HR, hardware, IG/LI metrics, training — see inventory §Independent.

## Importer rules (must hold before cutover)

1. Dry-run default; no wipe without backup.  
2. Idempotent re-import (no duplicate clients/IDs).  
3. Year counters reset correctly (`SWA-{year}-…`).  
4. Duplicate client = **reuse**, not silent second row.

## Evidence to attach when green

- `artifacts/playwright/seal/*.zip` director path  
- Import dry-run log path + exit code  
- Count of rows imported vs inventory est.

**Seal rule:** every inventory row is **mapped** or **explicit GAP accepted by director** — no silent drops.
