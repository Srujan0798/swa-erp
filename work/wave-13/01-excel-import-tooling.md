# Task 01 — Excel → ERP data migration importer

## What to do
Build a CLI import tool (openpyxl-based, per Meeting 2's confirmed stack) that reads the client's
21 source Excel sheets and loads them into the ERP as the one-time go-live migration. Per
`docs/decisions/0002-core-id-chain-gap.md` item #9: dev team builds the tool, internal admin
runs it and owns the resulting data — this task is scoped to the TOOL only, not running it
against real client data (that happens later, out of band, once wave-9 ships and real files are
shared).

**Depends on wave-9 (Inquiry/Agreement/Token/DocumentReference models must exist) and wave-10
(SustainabilityMetric).** Do not start until those land.

## Files to create
- CREATE: `scripts/import_excel.py` — CLI entrypoint, one subcommand per sheet type
  (`clients`, `inquiries`, `agreements`, `tokens`, `document_references`, `projects`,
  `time_logs`, `sustainability`)
- CREATE: `src/backend/services/import_service.py` — parsing + validation + upsert logic,
  callable from the CLI and reusable if a future admin-UI import screen is built
- CREATE: `tests/wave-13/test_import_service.py` — use small synthetic `.xlsx` fixtures, not
  real client data (which isn't available to this task)
- CREATE: `tests/wave-13/fixtures/` — synthetic sample sheets matching the column layouts in
  `resources/EXCEL_SHEETS_INVENTORY.md`

## Files to modify
- MODIFY: `Makefile` — add `make import-data file=<path> type=<sheet-type>` target
- MODIFY: `requirements.txt` — confirm `openpyxl` is present (should already be, per stack)

## Files you must NOT touch
- Do not attempt to fetch or fabricate real client data
- Do not modify any wave-9/10 model files — this task reads their schemas, doesn't change them

## The core problem (inline)
Column layouts below are read directly from the actual files in
`resources/ERP_Sheets_Extracted/ERP Sheets/*.xlsx` (verified with openpyxl, not copied from the
inventory doc, which was itself found to have gaps — cross-check the live files if anything here
looks off):

- **Inquiries Sheet.xlsx**: Sr No, Inquiry ID, Inquiry Date, Inquiry Type, Inquiry Source,
  Client Name, Requirement Summary, Estimated Value, Priority, Status, Owner, Technical Lead,
  Notes → maps to `Inquiry` (wave-9). Sample IDs: `SWA-2025-INQ-001`.
- **Clients Sheet.xlsx**: Sr No, Client ID, Client Name, Industry, Date Onboarded, Primary
  Contact, Email, Phone, Billing Address, Client Status, First Lead ID, First Inquiry ID, Notes
  → maps to patched `Client` (wave-9 task 01). Sample IDs: `SWA-2025-CLT-001`. **`First Lead
  ID` uses a `SWA-{year}-LDI-{seq}` format, not `INQ`** — per ADR-0002 item #6, treat this as a
  legacy alias for the same Inquiry record and resolve `LDI-*` values against `Inquiry` rows
  during import (best-effort match on date + client name if a direct ID map isn't available;
  report unresolved rows rather than guessing silently).
- **Service Agreements Sheet.xlsx**: Sr No, Agreement ID, Client Name, Client ID, Inquiry ID,
  Service Name, Start Date, End Date, Total Tokens, Status, Notes → maps to `ServiceAgreement`
  (wave-9). Sample IDs: `SWA-2025-SA-011`. `Service Name` is free text (e.g. `"INSUDESIGN"`).
- **Tokens Sheet.xlsx**: Sr. No., Date, Token ID, Agreement ID, Token Type, Description, Token
  Status, Tokens Used, Swa Employee Name/Team Leader, Project Owner, Client Employee Name →
  maps to `Token` (wave-9). Sample IDs: `SWA-2025-TKN-001`.
- **Document Reference Sheet.xlsx** (sheet name `DRN Sheet`): Sr. No., Date, DRN, Associated
  Project ID, Author, Document Type, Type, User, Description, Revision, Status, Remarks → maps
  to `DocumentReference` (wave-9). Note: this file has two inconsistent header rows in the same
  sheet (one says `Associated Project ID`, another `Associated Project/Token ID`) — import
  against `project_id` first, and set `token_id` only if the value resolves to an existing
  Token, otherwise leave it null and continue (don't fail the row).
- **Sustainability Metrics Sheet.xlsx**: Sr No, Date, Reference ID, Compliant with Green
  Standards (Yes/No), Total Energy Saved (kWh), CO2 emissions avoided (tCO2e), Lifecycle Cost
  savings delivered (INR), Insulation Efficiency (Actual/Expected), Payback Period (Months) →
  maps to `SustainabilityMetric` (wave-10). Sample `Reference ID`: `SWA-2025-PRJ-065`.
- **Project Tracking Sheet.xlsx** (sheet name `Project Tracking`): Sr. No., Project ID, Client
  ID, Inquiry ID, Client Name, Project Name, Start date, End date, Milestone, Progress
  Indicators, Status Updates, Team Leader, Project owner, Notes → maps to existing `Project`.
- **Time Logging Sheet.xlsx**: Sr. No., Date, Employee Name, Employee Role, Work Type,
  Reference ID, Revision, Project Name, Activity Type, Software Used, Work Mode, Hours Logged,
  Billable Hours, Remarks → maps to `TimeEntry` (existing wave-7 model — check
  `src/backend/models/time_tracking.py` for exact current field names before mapping; per
  ADR-0002 item #8, `Reference ID` is documented in the sheet itself as polymorphic — "primary
  linkage with project or token or Doc etc" — so resolve it against Project, then Token, then
  DocumentReference in that order and record which type matched).
- **Employees Sheet.xlsx**: minimal fields only per Meeting 1's HR-drop decision — `Employee_ID`
  (`SWA-2025-EMP-001` format), `Employee_Name`, `Department`, `Role`, `Reporting_Manager`. Do
  NOT import the HR-sensitive columns present in the real sheet (Gender, DOB, Race/Ethnicity,
  Disability/Neurodiversity, Socioeconomic) — those are explicitly out of MVP scope
  (Meeting 1 §4: HR/Admin restricted, drop from MVP) and there is no `Employee` model field for
  them; the importer must skip those columns entirely, not just leave them unmapped.

### Import behavior requirements
- Dry-run mode by default (`--dry-run`, prints what WOULD be created, no writes) — real writes
  require explicit `--commit` flag. This is a one-shot migration into a system that becomes
  source of truth; a silent partial-write on bad input is unacceptable.
- Row-level validation errors are collected and reported at the end (which rows failed and why),
  not fail-fast on the first bad row — a 500-row sheet with 3 bad rows should still import the
  other 497 and report the 3.
- Idempotent: re-running the same file twice must not create duplicates (match on the sheet's
  natural key — e.g. TokenID, DRN — upsert, don't insert blindly).
- Foreign key resolution: e.g. a Token row's `AgreementID` must resolve to an already-imported
  ServiceAgreement — if sheets are imported out of dependency order, fail that row with a clear
  "referenced AgreementID not found" message, don't crash the whole run.

## Acceptance criteria
- [ ] `python3 -m pytest tests/wave-13/ -q` passes using synthetic fixtures
- [ ] `python3 scripts/import_excel.py tokens tests/wave-13/fixtures/tokens_sample.xlsx --dry-run` prints a preview, writes nothing
- [ ] Same command with `--commit` writes rows; running it a second time with `--commit` creates zero duplicates
- [ ] A deliberately malformed row in a fixture is reported by row number, doesn't abort the rest of the import

## How to deliver
1. Implement import_service.py + CLI + synthetic fixtures + tests
2. Run acceptance commands
3. Write report to `work/reports/wave-13/01-excel-import-tooling.report.md`, including a short
   "how to run this against real client data" note for the internal admin who will own that step
4. Stop

## Constraints
- Time budget: 120 min
- Never write real client PII into fixtures or test output — synthetic data only
- No new dependencies beyond openpyxl (already in stack)
- Allowed tools: file edit, pytest, python
