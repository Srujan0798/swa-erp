# Task 01 — Task Models & CRUD API

## Goal
Create the Task and TaskComment SQLAlchemy models, Pydantic schemas, CRUD API endpoints, and Alembic migration for per-project task management. Tasks belong to a project and can have comments from any user.

## Files to Create/Modify

### 1. Models
Create `src/backend/models/task.py`:
```python
class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="todo")
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="medium")
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Constraints: status in ('todo', 'in_progress', 'done'), priority in ('low', 'medium', 'high', 'critical')

class TaskComment(Base):
    __tablename__ = "task_comments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```

Register both models in `src/backend/models/__init__.py`.

### 2. Schemas
Create `src/backend/schemas/task.py`:
- `TaskStatus(StrEnum)` — todo, in_progress, done
- `TaskPriority(StrEnum)` — low, medium, high, critical
- `TaskCreate` — title (required), description, priority (default medium), assignee_id, due_date
- `TaskUpdate` — title, description, priority, assignee_id, due_date (all optional)
- `TaskRead` — all fields + assignee_name (joined), created_by_name (joined), comment_count
- `TaskListResponse` — paginated: items, total, page, page_size
- `TaskCommentCreate` — content (required, min_length=1)
- `TaskCommentRead` — all fields + user_name (joined)

### 3. Repository
Create `src/backend/db/repositories/task_repo.py`:
- `create_task(db, project_id, title, description, priority, assignee_id, due_date, created_by)` → Task
- `get_by_id(db, task_id)` → Task | None (with eager-loaded assignee, creator, comments)
- `list_by_project(db, project_id, page, page_size, status, assignee_id, priority)` → tuple[list, total]
- `list_my_tasks(db, user_id, page, page_size)` → tuple[list, total] — tasks where assignee_id = user_id, across all projects, exclude deleted
- `update_task(db, task_id, **fields)` → Task | None
- `soft_delete(db, task_id)` → bool
- `get_task_counts_by_project(db, project_id)` → dict — counts by status
- `create_comment(db, task_id, user_id, content)` → TaskComment
- `list_comments(db, task_id)` → list[TaskComment]

### 4. Service
Create `src/backend/services/task_service.py`:
- `create_task_service(db, project_id, body, created_by)` → TaskRead — create task, write audit log `task.create`
- `get_task_service(db, task_id)` → TaskRead
- `list_tasks_service(db, project_id, page, page_size, status, assignee_id, priority)` → tuple
- `list_my_tasks_service(db, user_id, page, page_size)` → tuple
- `update_task_service(db, task_id, body, user_id)` → TaskRead — write audit log `task.update`
- `delete_task_service(db, task_id, user_id)` → bool — write audit log `task.delete`
- `add_comment_service(db, task_id, user_id, content)` → TaskCommentRead — write audit log `task.comment`
- `get_task_counts_service(db, project_id)` → dict

### 5. API
Create `src/backend/api/tasks.py`:
- `POST /api/projects/{project_id}/tasks` — create task. Require admin or PM role.
- `GET /api/projects/{project_id}/tasks` — list tasks with filters: status, assignee_id, priority, page, page_size
- `GET /api/projects/{project_id}/tasks/stats` — task counts by status
- `GET /api/tasks/{task_id}` — get task detail with comments
- `PATCH /api/tasks/{task_id}` — update task fields
- `DELETE /api/tasks/{task_id}` — soft delete
- `POST /api/tasks/{task_id}/comments` — add comment
- `GET /api/tasks/{task_id}/comments` — list comments
- `GET /api/tasks/my-tasks` — list tasks assigned to current user across all projects
- Register router in `src/backend/main.py`

### 6. Migration
Create `src/backend/alembic/versions/0006_add_tasks.py`:
- CREATE TABLE tasks with all columns and indexes
- CREATE TABLE task_comments with all columns and indexes
- Add unique constraint or index on (project_id, title) if needed

## Files you must NOT touch
- `src/backend/models/project.py` — do not modify existing project model
- `src/backend/models/user.py` — do not modify
- `src/backend/api/projects.py` — do not modify existing project endpoints
- `src/frontend/` — frontend changes are in task 04

## Acceptance criteria
- [ ] `Task` model has all required fields with correct types and constraints
- [ ] `TaskComment` model has all required fields
- [ ] Both models registered in `src/backend/models/__init__.py`
- [ ] CRUD endpoints return correct response codes (201 create, 200 get/update, 204 delete, 404 not found)
- [ ] RBAC enforced: only admin/PM can create tasks; assignee or admin can update
- [ ] Pagination works with page/page_size params
- [ ] Filter by status, assignee_id, priority on list endpoint
- [ ] Soft delete sets deleted_at, excludes from list queries
- [ ] Comments can be added by any authenticated user
- [ ] Task counts endpoint returns correct per-status counts
- [ ] My Tasks endpoint returns only tasks assigned to current user
- [ ] `pytest tests/wave-4/test_task_crud.py` passes
- [ ] `make lint` clean

## Test file
Create `tests/wave-4/test_task_crud.py` with at least:
- `test_create_task` — create task, verify fields in response
- `test_get_task` — create and retrieve by ID
- `test_list_tasks_pagination` — create 3 tasks, verify page 1 returns 2, total=3
- `test_filter_by_status` — create tasks with different statuses, filter
- `test_filter_by_priority` — filter by priority level
- `test_update_task` — update title and priority, verify changes persisted
- `test_soft_delete` — delete task, verify excluded from list but still in DB
- `test_create_comment` — add comment to task, verify user_name returned
- `test_list_comments` — add 3 comments, verify returned in order
- `test_task_counts_by_project` — create tasks in different statuses, verify counts
- `test_my_tasks` — create tasks with different assignees, verify filtering
- `test_create_task_unauthorized` — viewer role cannot create, expect 403
- `test_get_nonexistent_task` — expect 404

## Notes
- Follow existing patterns in `src/backend/models/project.py` and `src/backend/api/projects.py`
- Use `StrEnum` for status and priority (Python 3.11+)
- All monetary fields use `Decimal(18,2)` — not applicable here but keep in mind for future
- Soft-delete pattern matches existing Project model
- Migration number 0006 follows wave-3's 0004/0005 (check existing migrations to confirm)
