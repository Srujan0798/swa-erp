# Wave-4 Tasks — Task Management

## Task 1: Task Models & CRUD API
**File:** `work/wave-4/01-task-models-api.md`

**Goal:** Implement SQLAlchemy models, repositories, and FastAPI CRUD endpoints for tasks.

**Acceptance:**
- `Task`, `TaskDependency`, `TaskComment` models with FKs, indexes
- Alembic migration auto-generated
- Repository: `create, get, list, update, delete, list_by_project, list_by_assignee`
- API: `POST/GET/PATCH/DELETE /api/projects/{project_id}/tasks`, `GET /api/tasks/{task_id}`
- RBAC: PM/Designer create; Assignee update status; Viewer read-only
- Optimistic locking via `version` column (409 on conflict)
- Filters: `status`, `assignee_id`, `due_before`, `due_after`

**Files to Create/Modify:**
- `src/backend/models/task.py`
- `src/backend/db/repositories/task_repo.py`
- `src/backend/schemas/task.py`
- `src/backend/api/tasks.py`
- `src/backend/services/task_service.py`
- Alembic migration

**Skills:** `tdd`, `code-review`, `fastapi-crud`, `sqlalchemy-models`

---

## Task 2: Task Dependencies API
**File:** `work/wave-4/02-task-dependencies-api.md`

**Goal:** Implement DAG-based task dependencies with cycle detection.

**Acceptance:**
- `POST /api/tasks/{task_id}/dependencies` — add dependency
- `DELETE /api/tasks/{task_id}/dependencies/{dep_id}` — remove
- `GET /api/tasks/{task_id}/dependencies` — list (direct + transitive)
- Cycle detection: reject if adding creates cycle (400)
- Blocked status: task cannot move to `in_progress` if any dependency not `done`
- Transitive closure query for "all blockers" / "all blocked"

**Files to Create/Modify:**
- `src/backend/db/repositories/task_dependency_repo.py`
- `src/backend/services/task_dependency_service.py`
- `src/backend/api/task_dependencies.py`
- `src/backend/schemas/task_dependency.py`

**Skills:** `tdd`, `code-review`, `dag-validation`, `graph-algorithms`

---

## Task 3: Task Comments & Notifications
**File:** `work/wave-4/03-task-comments-notifications.md`

**Goal:** Threaded comments on tasks + in-app/email notifications.

**Acceptance:**
- `POST/GET /api/tasks/{task_id}/comments` — CRUD comments
- Threaded replies (parent_comment_id)
- Celery task: `send_task_notification_email` (assignment, status change, due soon, comment mention)
- In-app notification table + API `GET /api/notifications`
- Email template: task title, link, action required
- Debounce: batch notifications within 5 min

**Files to Create/Modify:**
- `src/backend/models/notification.py`
- `src/backend/db/repositories/notification_repo.py`
- `src/backend/services/notification_service.py`
- `src/backend/workers/notification_worker.py`
- `src/backend/api/notifications.py`
- Email templates: `templates/emails/task_assigned.html`, etc.

**Skills:** `tdd`, `code-review`, `email-notification`, `celery-worker`

---

## Task 4: Frontend Kanban Board
**File:** `work/wave-4/04-frontend-kanban-board.md`

**Goal:** Drag-drop Kanban board per project.

**Acceptance:**
- Route: `/projects/:projectId/kanban`
- Columns: `todo`, `in_progress`, `review`, `done` (configurable)
- Cards: title, assignee avatar, due date badge (red if overdue), priority indicator
- Drag-drop: `@dnd-kit` — move between columns, reorder within column
- Optimistic update → API sync → rollback on error (toast)
- "Add Task" button per column → opens TaskCreateForm
- Filter bar: assignee, status, due date range
- Virtualized list for >100 tasks
- Keyboard accessible (ARIA)

**Files to Create/Modify:**
- `src/frontend/src/pages/KanbanBoard.tsx`
- `src/frontend/src/components/tasks/KanbanColumn.tsx`
- `src/frontend/src/components/tasks/TaskCard.tsx`
- `src/frontend/src/components/tasks/TaskCreateForm.tsx`
- `src/frontend/src/hooks/useTasks.ts`
- `src/frontend/src/hooks/useKanban.ts`

**Skills:** `tdd`, `code-review`, `react-dnd`, `tailwind`, `tanstack-query`

---

## Task 5: Frontend Task Detail Modal
**File:** `work/wave-4/05-frontend-task-detail.md`

**Goal:** Task detail view with comments, dependencies, time-log link.

**Acceptance:**
- Click card → modal opens (shadcn/ui Dialog)
- Tabs: Details | Comments | Dependencies | Time Log
- Details: title, description, assignee, due, priority, status, dates
- Comments: threaded list, add reply, mention user (@name)
- Dependencies: list blockers/blocked, "Add Blocker" button
- Time Log: "Log Time" button → opens Wave-7 time entry with task ref prefilled
- Edit button → inline edit (title, desc, assignee, due, priority)
- Delete button (confirm)
- Real-time updates via React Query invalidation

**Files to Create/Modify:**
- `src/frontend/src/components/tasks/TaskDetailModal.tsx`
- `src/frontend/src/components/tasks/TaskComments.tsx`
- `src/frontend/src/components/tasks/TaskDependencies.tsx`
- `src/frontend/src/hooks/useTaskDetail.ts`

**Skills:** `tdd`, `code-review`, `react-hook-form`, `zod`, `shadcn-ui`

---

## Contract Test Files (Pytest)

Each task has a corresponding contract test in `.specify/specs/wave-4/contracts/`:

| Test File | Covers |
|-----------|--------|
| `test_tasks_api.py` | Task 1 |
| `test_task_dependencies.py` | Task 2 |
| `test_task_comments.py` | Task 3 |
| `test_kanban.py` | Task 4 |
| `test_task_notifications.py` | Task 3 (notifications) |