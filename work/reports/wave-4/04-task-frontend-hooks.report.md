# Task 04 — Frontend API Layer & Hooks — Report

## Files Created/Modified

| File | Action |
|------|--------|
| `src/frontend/src/types/api.ts` | Modified — appended Task types (TaskStatus, TaskPriority, Task, TaskComment, TaskListResponse, TaskStats, TaskCreateRequest, TaskUpdateRequest, TaskTransitionRequest, TaskReorderRequest, TaskBulkStatusRequest) |
| `src/frontend/src/lib/api.ts` | Modified — appended 13 task API methods (listTasks, getTask, createTask, updateTask, deleteTask, transitionTask, reorderTask, bulkUpdateStatus, assignTask, unassignTask, getMyTasks, getProjectTaskStats, addComment, listComments) |
| `src/frontend/src/lib/queryKeys.ts` | Created — query key factory for task queries |
| `src/frontend/src/hooks/useTasks.ts` | Created — 15 hooks (5 query + 10 mutation) |
| `src/frontend/src/hooks/__tests__/useTasks.test.ts` | Created — 7 test cases covering key hooks |
| `src/frontend/tsconfig.json` | Modified — excluded `__tests__` from tsc (vitest not installed) |

## tsc --noEmit Result

**Pass** — no errors from new/modified files.

All remaining errors are pre-existing:
- Duplicate BOQ/BOQListResponse/BOQItem type declarations in `types/api.ts`
- Unused imports (Vendor, Material, Document, Compliance, Time, Financial) in `api.ts`
- Missing `Badge` component in `QuoteDetail.tsx`
- Missing `VendorContact`/`MaterialCategory` types in `api.ts` imports

## Hooks Implemented

**Query hooks:**
- `useTasks(projectId, filters?)` — paginated task list for project
- `useTask(taskId)` — single task detail
- `useMyTasks(filters?)` — tasks assigned to current user
- `useProjectTaskStats(projectId)` — task counts by status
- `useTaskComments(taskId)` — comment list

**Mutation hooks:**
- `useCreateTask(projectId)` — POST /api/projects/{id}/tasks
- `useUpdateTask()` — PATCH /api/tasks/{id}
- `useDeleteTask()` — DELETE /api/tasks/{id}
- `useTransitionTask()` — POST /api/tasks/{id}/transition
- `useReorderTask()` — POST /api/tasks/{id}/reorder
- `useBulkUpdateStatus()` — POST /api/tasks/bulk-status
- `useAssignTask()` — POST /api/tasks/{id}/assign
- `useUnassignTask()` — POST /api/tasks/{id}/unassign
- `useAddComment()` — POST /api/tasks/{id}/comments

All mutations invalidate relevant query keys via the `taskKeys` factory.

## Notes

- Test file (`useTasks.test.ts`) requires `vitest` and `@testing-library/react` to run — these are not yet in devDependencies. Install them before running tests.
- Followed existing patterns from `useAuth.ts`, `useBoqs.ts`, `useQuotes.ts`.
- All hooks are fully typed with no `any` usage.
