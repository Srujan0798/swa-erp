# Task 02 — BOQ Versioning & Item API

## Goal
Complete the BOQ API: list versions, view items, soft delete. Build the frontend data layer hooks.

## Files to Create/Modify

### 1. Repository Extensions
Extend `src/backend/db/repositories/boq_repo.py`:
- `get_version_with_items(db, boq_id)` — eager load items ordered by line_number
- `list_versions_with_counts(db, project_id, page, page_size)` — list versions with item count
- `count_items(db, boq_id)` — total line items for a version

### 2. Service Extensions
Extend `src/backend/services/boq_service.py`:
- `list_boq_versions(db, project_id, page=1, page_size=20)` — returns paginated list with item counts
- `get_boq_detail(db, boq_id)` — returns BOQ + all items
- `soft_delete_boq(db, boq_id, actor_id)` — soft delete + audit log

### 3. API Endpoints
Extend `src/backend/api/boqs.py`:
- `GET /api/projects/{project_id}/boqs` — list versions (admin/pm/designer/auditor/viewer can view)
  - Query params: `page`, `page_size`
  - Response: `BOQListResponse`
- `GET /api/boqs/{boq_id}` — get version detail
  - Response: `BOQRead` with nested `items: list[BOQItemRead]`
- `GET /api/boqs/{boq_id}/items` — get paginated items
  - Query params: `page`, `page_size`
  - Response: `{items: list[BOQItemRead], total: int, page, page_size}`
- `DELETE /api/boqs/{boq_id}` — soft delete (admin/pm only)
  - Return 204

### 4. Schemas
Extend `src/backend/schemas/boq.py`:
- `BOQRead` should include `items: list[BOQItemRead]` (optional, for detail view)
- `BOQItemRead` should include all fields
- `BOQItemListResponse` for paginated items

### 5. Frontend API Layer
Extend `src/frontend/src/lib/api.ts`:
```typescript
listBoqs: (projectId: string, params?: { page?: number; page_size?: number }) => ...
getBoq: (id: string) => ...
getBoqItems: (id: string, params?: { page?: number; page_size?: number }) => ...
uploadBoq: (projectId: string, file: File, notes?: string) => ...
deleteBoq: (id: string) => ...
```

### 6. Frontend Hooks
Create `src/frontend/src/hooks/useBoqs.ts`:
- `useBoqs(projectId, page?, pageSize?)` — list query
- `useBoq(boqId)` — detail query
- `useBoqItems(boqId, page?, pageSize?)` — items query
- `useUploadBoq()` — mutation
- `useDeleteBoq()` — mutation

## Acceptance Criteria
- [ ] Can list all BOQ versions for a project with pagination
- [ ] Can view any version's line items with pagination
- [ ] Can soft delete a version; it no longer appears in list
- [ ] Viewer can view but not delete
- [ ] `pytest tests/wave-3/test_boq_versions.py` passes

## Test File
Create `tests/wave-3/test_boq_versions.py` with at least:
- `test_list_versions` — upload 2 BOQs, list shows both
- `test_version_detail` — get detail includes all items
- `test_version_items_pagination` — 25 items, page_size=10 shows 10
- `test_soft_delete_version` — delete, then list doesn't include it
- `test_viewer_can_view_but_not_delete` — viewer gets 200 on GET, 403 on DELETE

## Notes
- Items should always be ordered by `line_number` ascending
- Soft-deleted versions should not appear in list but can still be referenced by existing quotes
- The `file_path` field should be exposed in detail view so frontend can offer download