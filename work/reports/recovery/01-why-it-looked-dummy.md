# Why SWA feedback said “dummy / not usable”

## Evidence

```
Recovery week-1 product diagnosis (static + UI code).
Fixes: DocumentReferencesPage, Sidebar Excel workflow, Dashboard chain,
make swa-live-local, VIRAJ_TRIAL_SCRIPT.md
```

## Evidence (detail)

```
# Diagnosed from codebase (2026-08-23 recovery week-1)
# - DocumentReferenceList only under Project; no global nav until this week
# - Sidebar weighted Vendors/RFQs equal to chain
# - Dashboard FLOW omitted Token / Doc Ref / Time
# - docs/REAL_DATA.md: Project Tracking sample often 0 rows
# - seed_demo.py labeled demo-seed / synthetic
```

## Root causes (product, not “missing pytest”)

1. **Wrong first-class object:** Excel “Document Reference Sheet” was buried; “Documents” meant file storage.
2. **Generic CRM chrome:** Commercial modules competed with the Excel chain in the nav.
3. **Dummy data path:** Easy to show `seed_demo` instead of `bootstrap-real` → fake names.
4. **Sparse sample:** Empty projects list after import looks “broken” without explanation.

## Week-1 fixes (this commit)

- Global **Document References** page + sidebar item **5. Document refs**
- Dashboard full chain + empty-state → `make bootstrap-real`
- Commercial demoted to **More**
- `make swa-live-local` alias + VIRAJ trial script

## Status

IN PROGRESS — Week 1 of 4 (see recovery plan).
