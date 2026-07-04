# Wave-4 Spec — Task Management

## Objective
Per-project task management with assignees, dependencies, statuses, due dates, and Kanban board.

---

## Scope (from PRD + Project Tracking Sheet)

| Feature | Details |
|---------|---------|
| **Task CRUD** | Create, read, update, delete tasks per project |
| **Assignees** | Assign to users (designer, auditor, PM) |
| **Dependencies** | Task A blocks Task B (DAG, no cycles) |
| **Statuses** | `todo` → `in_progress` → `review` → `done` (configurable) |
| **Due dates** | Optional, with overdue highlighting |
| **Kanban board** | Drag-drop columns per status |
| **Task comments** | Threaded discussion per task |
| **Notifications** | In-app + email on assignment, status change, due soon |

---

## Data Model (from Project Tracking Sheet + Time Logging)

```sql
-- tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'todo',
    priority INTEGER DEFAULT 0,  -- higher = more urgent
    assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,
    reporter_id UUID NOT NULL REFERENCES users(id),
    due_date TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    estimated_hours DECIMAL(6,2),
    actual_hours DECIMAL(6,2) DEFAULT 0,
    position INTEGER DEFAULT 0,  -- for Kanban ordering
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    version INTEGER NOT NULL DEFAULT 1  -- optimistic locking
);

-- task_dependencies (DAG)
CREATE TABLE task_dependencies (
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    depends_on_task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, depends_on_task_id)
);

-- task_comments
CREATE TABLE task_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_task_deps_task ON task_dependencies(task_id);
CREATE INDEX idx_task_deps_dep ON task_dependencies(depends_on_task_id);
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/projects/{project_id}/tasks` | Create task |
| GET | `/api/projects/{project_id}/tasks` | List tasks (filter: status, assignee, due) |
| GET | `/api/tasks/{task_id}` | Get task detail |
| PATCH | `/api/tasks/{task_id}` | Update task (optimistic lock) |
| DELETE | `/api/tasks/{task_id}` | Delete task |
| POST | `/api/tasks/{task_id}/dependencies` | Add dependency |
| DELETE | `/api/tasks/{task_id}/dependencies/{dep_id}` | Remove dependency |
| GET | `/api/tasks/{task_id}/dependencies` | List dependencies |
| POST | `/api/tasks/{task_id}/comments` | Add comment |
| GET | `/api/tasks/{task_id}/comments` | List comments |
| PATCH | `/api/tasks/{task_id}/reorder` | Kanban reorder (position) |
| GET | `/api/projects/{project_id}/tasks/kanban` | Kanban board (grouped by status) |

---

## Frontend Components

| Component | Description |
|-----------|-------------|
| `TaskKanbanBoard` | Drag-drop columns (todo/in_progress/review/done) |
| `TaskCard` | Title, assignee avatar, due badge, priority |
| `TaskDetailModal` | Full detail, comments, dependencies, time log link |
| `TaskCreateForm` | Title, description, assignee, due, priority, deps |
| `TaskDependencyGraph` | Visual DAG (optional, later) |

---

## Acceptance Criteria (Contracts)

1. **Create task** → appears in project's Kanban `todo` column
2. **Drag-drop** → status updates, position persists
3. **Assign user** → notification sent, appears in "My Tasks"
4. **Add dependency** → blocked task shows lock icon, cannot move to `in_progress` until dependency `done`
5. **Cycle detection** → API rejects circular dependency (400)
6. **Due date overdue** → red badge on card, dashboard alert
6. **Optimistic lock** → concurrent edit returns 409 with current version
7. **Comments** → threaded, real-time update via React Query invalidation
8. **RBAC** → PM/Designer can create; Assignee can update status; Viewer read-only
8. **Time logging link** → "Log Time" button opens Wave-7 time entry with task ref

---

## Test Files Required

| File | Tests |
|------|-------|
| `tests/wave-4/test_tasks_api.py` | CRUD, filters, RBAC |
| `tests/wave-4/test_task_dependencies.py` | DAG, cycle detection |
| `tests/wave-4/test_task_comments.py` | CRUD, threading |
| `tests/wave-4/test_kanban.py` | Reorder, status transitions |
| `tests/wave-4/test_task_notifications.py` | Assignment, due alerts |

---

## Tasks (5)

| # | Task File | Focus |
|---|-----------|-------|
| 1 | `work/wave-4/01-task-models-api.md` | Models, repos, CRUD API, RBAC |
| 2 | `work/wave-4/02-task-dependencies-api.md` | Dependency DAG, cycle detection, API |
| 3 | `work/wave-4/03-task-comments-notifications.md` | Comments, in-app/email notifications |
| 4 | `work/wave-4/04-frontend-kanban-board.md` | Kanban board, drag-drop, task cards |
| 5 | `work/wave-4/05-frontend-task-detail.md` | Task detail modal, comments, deps, time link |

---

## Skills Required per Task

| Task | Skills |
|------|--------|
| 01 | `tdd`, `code-review`, `fastapi-crud` |
| 02 | `tdd`, `code-review`, `dag-validation` |
| 03 | `tdd`, `code-review`, `email-notification` |
| 04 | `tdd`, `code-review`, `react-dnd`, `tailwind` |
| 05 | `tdd`, `code-review`, `react-hook-form`, `zod` |