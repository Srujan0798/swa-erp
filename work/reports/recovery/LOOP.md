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
