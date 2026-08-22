# Recovery loop log

## Fire — 2026-08-23 (field parity + UX hardening)

**Focus:** Excel field parity (Time Logging + Inquiry Technical Lead) + Doc Refs / Login / Dashboard / real-data messaging polish.

**Commit:** `cb1f07f` (pushed to `origin/main`)

### Changed

1. **Time Logging Sheet parity (end-to-end)**
   - Migration `0031`: `employee_name`, `employee_role`, `work_type`, `sheet_reference_id`, `revision`, `activity_type`, `software_used`, `work_mode`, `billable_hours` on `time_entries`
   - Model / Pydantic schemas / `time_service` read path
   - Import no longer mashes employee/activity into description; maps Excel columns properly
   - UI: `TimeTrackingPage`, `TimeEntryForm`, `TimeEntryList` show Excel-style columns
   - API test: `test_create_time_entry_excel_fields`

2. **Inquiry Technical Lead**
   - Column `technical_lead` (free-text, Excel reality) + import mapping
   - Form / list / detail UI

3. **Document References page excellence**
   - Columns: DRN, Date, Doc type, Type, Rev, Status, User, Description, Project
   - Doc-type filter; clearer empty-state → `make swa-live-local` / Project create path
   - Copy distinguishes Files/drawings vs Doc Ref Sheet

4. **Chain-first UX / real-data default story**
   - Login hint: `make swa-live-local`
   - Dashboard: time counts; sparse-projects banner; empty-state uses `swa-live-local`
   - Sidebar footer → `make swa-live-local`
   - Makefile / `docs/REAL_DATA.md` / `VIRAJ_TRIAL_SCRIPT.md` aligned

### Evidence

```
# Frontend (touched)
cd src/frontend && npm test -- --run \
  TimeEntryList TimeTrackingPage LoginPage DocumentReferenceList \
  InquiryForm Sidebar InquiriesPage ProjectList
→ 8 files / 58+ passed

# Backend
pytest tests/wave-7/test_time_tracking.py tests/wave-13/ -q
→ 25 passed (incl. new excel fields test + import suite)
```

### Files (high level)

- `src/backend/alembic/versions/0031_*.py`
- `src/backend/models/{time_tracking,inquiry}.py`
- `src/backend/schemas/{time_tracking,inquiry}.py`
- `src/backend/services/{time_service,import_service}.py`
- `src/frontend/src/pages/{TimeTrackingPage,DocumentReferencesPage,DashboardPage,LoginPage,InquiriesPage,InquiryDetailPage}.tsx`
- `src/frontend/src/components/{time/*,inquiries/InquiryForm,layout/Sidebar}.tsx`
- `Makefile`, `docs/REAL_DATA.md`, `deliverables/VIRAJ_TRIAL_SCRIPT.md`

### Next

- Tokens list: surface SWA employee name more clearly if missing in global list
- Apply `alembic upgrade` on live local DB before Viraj trial
- Remaining Week-2/3: more Doc Ref author picker UX; Time employee name default from session user

### Stop-loop checklist

| Criterion | Status |
|-----------|--------|
| Doc Refs excellent | improved (sheet columns visible) |
| Chain-first nav/dashboard | yes |
| Convert + empty project paths | yes (prior + sparse banner) |
| Real-data boot default story | yes (`swa-live-local`) |
| VIRAJ_TRIAL_SCRIPT accurate | updated |
| No Accme/demo-first path | yes |
| Pushed to origin | yes (`cb1f07f`) |

## Fire — 2026-08-23 (Tokens/SA/DocRef Excel names)

**Focus:** Tokens Sheet employee names (import gap fix) + Service Agreements list excellence + Doc Ref Author + Time employee default.

**Commit:** `eaaf12d` (docs follow-up `8ccf21e`; pushed to `origin/main`)

### Changed

1. **Tokens Excel name parity**
   - Migration `0032`: `swa_employee_name`, `project_owner_name` on `tokens`
   - Import always stores sheet names (previously dropped when no system user matched)
   - TokenForm + TokensPage + TokensList show SWA employee / client employee
   - API test: `test_create_stores_excel_employee_names`

2. **Document Reference Author**
   - Migration `0032`: `author_name` on `document_references`
   - Import stores Author text; form/list/global page show Author column

3. **Service Agreements page**
   - Excel sheet copy; End date + Notes columns
   - API enriches `client_name` for Client Name column (sheet mental model)
   - Empty-state → `make swa-live-local`

4. **Time logging**
   - Employee name field defaults from signed-in user

5. **VIRAJ_TRIAL_SCRIPT** updated for SA/Tokens/DocRef column talk-track

### Evidence

```
pytest tests/wave-9/ -q → 79 passed
pytest tests/wave-13/test_import_service.py → 12 passed
frontend TokensPage/TokensList/DocRefList/TimeTracking → 32 passed
```

### Next / residual

- Apply `alembic upgrade head` when postgres is up (`make swa-live-local` recreates via create path / bootstrap)
- Optional: agreement_id visible on Tokens global list

### Stop-loop checklist

| Criterion | Status |
|-----------|--------|
| Doc Refs excellent | yes (Author + sheet columns) |
| Chain-first nav/dashboard | yes |
| Convert + empty project paths | yes |
| Real-data boot default story | yes |
| VIRAJ_TRIAL_SCRIPT accurate | yes |
| No Accme/demo-first path | yes |
| Pushed to origin | yes (`eaaf12d` / `8ccf21e`) |
