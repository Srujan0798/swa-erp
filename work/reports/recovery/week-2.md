# Recovery week-2 — Projects empty-state + convert UX

**Date:** 2026-08-23  
**Focus:** (B) Project empty-state when Project Tracking has 0 rows; Inquiry convert lands on Project.

## Evidence

```
cd src/frontend && npm test -- --run \
  src/components/projects/__tests__/ProjectList.test.tsx \
  src/components/inquiries/__tests__/ConvertToClientButton.test.tsx
Test Files  2 passed (2)
Tests  11 passed (11)
```

## Done this fire

1. **Projects empty-state** (`ProjectList.tsx`)
   - Explains sample **Project Tracking** sheet often has **0 rows** after `make bootstrap-real` (expected).
   - Writers: link to **Inquiries** (Meeting 2 convert) + create project.
   - Viewers: ask a PM.
   - Subtitle names the Excel sheet.

2. **Convert UX copy + test** (`ConvertToClientButton`)
   - Dialog copy states Meeting 2 rule: check client → always land on Project.
   - Test now asserts navigate to `/projects/:id` after reusing an existing client (300 → select → success).

3. **Frontend tests** for `ProjectList` + `ConvertToClientButton` updated.

## Already true from week-1 (unchanged)

- Doc Refs route `/document-references` + Sidebar **5. Document refs**
- Dashboard chain + bootstrap empty-state
- Commercial under **More**
- README / `make swa-live-local` real-data first path (no demo-first)

## Next

- (C) Field-parity start for Doc Ref / Time sheets vs Excel columns
- (D) Polish `VIRAJ_TRIAL_SCRIPT` + run notes after a real `swa-live-local` pass
- (E) Keep pushing coherent chunks

## Status

IN PROGRESS — Week 2 of 4.
