# Task 04 — Frontend API Layer & Hooks

## Goal
Add TypeScript types for Task and TaskComment, API methods for all task endpoints, and React hooks using TanStack Query for task CRUD, transitions, and board data.

## Files to Create/Modify

### 1. TypeScript Types
Update `src/frontend/src/types/api.ts`:
```typescript
export type TaskStatus = "todo" | "in_progress" | "done";
export type TaskPriority = "low" | "medium" | "high" | "critical";

export interface Task {
  id: string;
  project_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  assignee_id: string | null;
  due_date: string | null;
  sort_order: number;
  created_by: string;
  created_at: string;
  updated_at: string;
  assignee_name: string | null;
  created_by_name: string;
  comment_count: number;
}

export interface TaskComment {
  id: string;
  task_id: string;
  user_id: string;
  content: string;
  created_at: string;
  user_name: string;
}

export interface TaskListResponse {
  items: Task[];
  total: number;
  page: number;
  page_size: number;
}

export interface TaskStats {
  todo: number;
  in_progress: number;
  done: number;
  total: number;
}

export interface TaskCreateRequest {
  title: string;
  description?: string;
  priority?: TaskPriority;
  assignee_id?: string;
  due_date?: string;
}

export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  priority?: TaskPriority;
  assignee_id?: string;
  due_date?: string;
}

export interface TaskTransitionRequest {
  to_status: TaskStatus;
}

export interface TaskReorderRequest {
  status: TaskStatus;
  sort_order: number;
}

export interface TaskBulkStatusRequest {
  task_ids: string[];
  new_status: TaskStatus;
}
```

### 2. API Methods
Update `src/frontend/src/lib/api.ts`:
```typescript
// Add to api object:
listTasks: (projectId: string, params?: { page?: number; page_size?: number; status?: string; assignee_id?: string; priority?: string }) => ...
getTask: (taskId: string) => ...
createTask: (projectId: string, data: TaskCreateRequest) => ...
updateTask: (taskId: string, data: TaskUpdateRequest) => ...
deleteTask: (taskId: string) => ...
transitionTask: (taskId: string, toStatus: TaskStatus) => ...
reorderTask: (taskId: string, status: TaskStatus, sortOrder: number) => ...
bulkUpdateStatus: (data: TaskBulkStatusRequest) => ...
assignTask: (taskId: string, assigneeId: string) => ...
unassignTask: (taskId: string) => ...
getMyTasks: (params?: { page?: number; page_size?: number; status?: string; priority?: string }) => ...
getProjectTaskStats: (projectId: string) => ...
addComment: (taskId: string, content: string) => ...
listComments: (taskId: string) => ...
```

### 3. React Hooks
Create `src/frontend/src/hooks/useTasks.ts`:
```typescript
// Query hooks (TanStack Query):
export function useTasks(projectId: string, filters?: TaskFilters) — list tasks for project
export function useTask(taskId: string) — get single task with comments
export function useMyTasks(filters?: TaskFilters) — list tasks assigned to current user
export function useProjectTaskStats(projectId: string) — task counts by status
export function useTaskComments(taskId: string) — list comments

// Mutation hooks:
export function useCreateTask(projectId: string) — create task, invalidate project tasks query
export function useUpdateTask() — update task, invalidate affected queries
export function useDeleteTask() — soft delete, invalidate queries
export function useTransitionTask() — change status, invalidate queries
export function useReorderTask() — move task within/across columns
export function useBulkUpdateStatus() — bulk status change
export function useAssignTask() — assign user to task
export function useUnassignTask() — unassign user from task
export function useAddComment() — add comment to task
```

All mutation hooks should:
- Use `useMutation` from TanStack Query
- Call `queryClient.invalidateQueries` on success to refetch affected data
- Return `{ mutate, mutateAsync, isLoading, error }` pattern

### 4. Query Key Factory
Create `src/frontend/src/lib/queryKeys.ts`:
```typescript
export const taskKeys = {
  all: ["tasks"] as const,
  lists: () => [...taskKeys.all, "list"] as const,
  list: (projectId: string, filters?: TaskFilters) => [...taskKeys.lists(), projectId, filters] as const,
  details: () => [...taskKeys.all, "detail"] as const,
  detail: (taskId: string) => [...taskKeys.details(), taskId] as const,
  myTasks: (filters?: TaskFilters) => [...taskKeys.all, "my", filters] as const,
  stats: (projectId: string) => [...taskKeys.all, "stats", projectId] as const,
  comments: (taskId: string) => [...taskKeys.all, "comments", taskId] as const,
};
```

## Files you must NOT touch
- `src/frontend/src/types/api.ts` — append only, do not modify existing types
- `src/frontend/src/lib/api.ts` — append only to api object
- `src/backend/` — backend is complete from tasks 01-03

## Acceptance criteria
- [ ] All TypeScript types match backend schema shapes
- [ ] API methods use correct HTTP methods and endpoints
- [ ] API methods handle query params properly (URLSearchParams)
- [ ] useTasks hook returns paginated task list
- [ ] useMyTasks hook calls /api/tasks/my-tasks
- [ ] useCreateTask mutation invalidates task list queries after success
- [ ] useTransitionTask mutation updates task status
- [ ] useReorderTask mutation updates sort_order
- [ ] useAssignTask mutation sets assignee
- [ ] All hooks have proper TypeScript types (no `any`)
- [ ] Query key factory follows consistent pattern
- [ ] `npx tsc --noEmit` passes (TypeScript check)
- [ ] `npm run lint` clean

## Test file
Create `src/frontend/src/hooks/__tests__/useTasks.test.ts` with at least:
- `test useTasks returns task list` — mock API, verify data shape
- `test useCreateTask calls POST` — verify correct endpoint and body
- `test useUpdateTask calls PATCH` — verify correct endpoint
- `test useTransitionTask calls POST /transition` — verify body shape
- `test useMyTasks calls correct endpoint` — verify /api/tasks/my-tasks
- `test useProjectTaskStats calls correct endpoint` — verify /api/projects/{id}/tasks/stats
- `test mutations invalidate queries` — verify queryClient.invalidateQueries called

Use Vitest + React Testing Library pattern. Mock the `api` module.

## Notes
- Follow existing hook patterns in `src/frontend/src/hooks/useDashboard.ts`
- Follow existing API patterns in `src/frontend/src/lib/api.ts`
- TanStack Query v5 uses `useQuery` with `queryKey` and `queryFn` pattern
- Ensure all hooks work with strict TypeScript mode
- Query keys must be structured for effective cache invalidation
- Do not add any UI components — that's task 05
