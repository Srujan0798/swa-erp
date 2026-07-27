# Task 02 — BOQ Versioning & Item API — Report

## Files Created/Modified

### Backend (Python)
1. `src/backend/models/boq.py` — BOQ + BOQItem SQLAlchemy models (Task 01 base)
2. `src/backend/schemas/boq.py` — Pydantic schemas with `BOQListRead` (item_count), `BOQItemListResponse`, `BOQRead` (file_path + items)
3. `src/backend/db/repositories/boq_repo.py` — Repository with `count_items`, `list_versions_with_counts`, `list_items_paginated` (Task 02 extensions)
4. `src/backend/services/boq_service.py` — Service with `list_boq_versions`, `get_boq_detail`, `get_boq_items_paginated`, `soft_delete_boq` (Task 02 extensions)
5. `src/backend/api/boqs.py` — Full API: POST upload, GET list versions, GET detail, GET paginated items, DELETE soft delete (admin/pm only)
6. `src/backend/models/__init__.py` — Already registered BOQ/BOQItem (from Task 01)
7. `src/backend/main.py` — Already registered boqs_router (from Task 01)
8. `src/backend/api/__init__.py` — Already registered boqs_router (from Task 01)

### Frontend (TypeScript)
9. `src/frontend/src/types/api.ts` — Added BOQ, BOQItem, BOQListRead, BOQListResponse, BOQItemListResponse types
10. `src/frontend/src/lib/api.ts` — Added listBoqs, getBoq, getBoqItems, uploadBoq, deleteBoq methods (from Task 01)
11. `src/frontend/src/hooks/useBoqs.ts` — Created useBoqs, useBoq, useBoqItems, useUploadBoq, useDeleteBoq hooks

### Tests
12. `tests/wave-3/test_boq_versions.py` — 5 tests: list versions, version detail, items pagination, soft delete, viewer permissions

## Ruff Result
All checks passed!

## Acceptance
- [x] `python3 -m pytest tests/wave-3/test_boq_versions.py -q` — 5 passed
- [x] `python3 -m ruff check` on all touched files — clean

## Notes
- Task 01 created the base BOQ files in parallel. Task 02 extensions were layered on top.
- Field naming follows Task 01 conventions: `version_number`, `file_name`, `parsed_by`, `parsed_at`, `rate` (not `unit_rate`).
- Soft delete uses `deleted_at` timestamp; soft-deleted versions excluded from list queries.
- Items ordered by `line_number` ascending in all item queries.
- `file_path` exposed in `BOQRead` for frontend download capability.
- Delete endpoint restricted to `Role.PM` (which includes admin via hierarchy).
