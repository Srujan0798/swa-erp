# Task 03 — Task Assignments & Notifications

## Goal
Implement task assignment/unassignment logic, filter tasks by assignee, My Tasks view across all projects, and task count statistics per project.

## Files to Create/Modify

### 1. Repository Updates
Update `src/backend/db/repositories/task_repo.py`:
- `assign_task(db, task_id, assignee_id)` → Task — set assignee_id, return updated task
- `unassign_task(db, task_id)` → Task — set assignee_id to None, return updated task
- `list_tasks_by_assignee(db, user_id, page, page_size, status, priority)` → tuple[list, total] — across all projects
- `get_task_counts_by_project(db, project_id)` → dict — `{todo: N, in_progress: N, done: N, total: N}`
- `get_task_counts_by_user(db, user_id)` → dict — task counts grouped by status, across all projects

### 2. Schemas
Update `src/backend/schemas/task.py`:
- `TaskAssign` — assignee_id: uuid.UUID (required)
- `TaskAssignResponse` — task_id, assignee_id, assignee_name
- `TaskStatsResponse` — todo: int, in_progress: int, done: int, total: int
- `MyTasksResponse` — items: list[TaskRead], total: int, stats: TaskStatsResponse

### 3. Service Updates
Update `src/backend/services/task_service.py`:
- `assign_task_service(db, task_id, assignee_id, user_id)` → TaskRead
  1. Verify task exists
  2. Verify assignee_id is a valid user (exists in users table)
  3. Update assignee_id
  4. Write audit log `task.assign` with assignee_id and assignee_name
  5. Return updated task with assignee_name
- `unassign_task_service(db, task_id, user_id)` → TaskRead
  1. Verify task exists and has an assignee
  2. Set assignee_id = None
  3. Write audit log `task.unassign`
  4. Return updated task
- `list_my_tasks_service(db, user_id, page, page_size, status, priority)` → MyTasksResponse
  1. Query tasks where assignee_id = user_id
  2. Include stats summary
  3. Return paginated results with stats
- `get_project_task_stats_service(db, project_id)` → TaskStatsResponse

### 4. API Updates
Update `src/backend/api/tasks.py`:
- `POST /api/tasks/{task_id}/assign` — body: `TaskAssign`, require admin or PM
- `DELETE /api/tasks/{task_id}/assign` — unassign, require admin or PM
- `GET /api/tasks/my-tasks` — list tasks assigned to current user, optional filters: status, priority
- `GET /api/projects/{project_id}/tasks/stats` — task counts by status for project (may already exist from task 01)

### 5. User Validation
In assignment logic, verify that the assignee_id refers to an existing active user:
- Query `User` model where `id = assignee_id` and `is_active = True`
- Return 400 if user not found or inactive

## Files you must NOT touch
- `src/backend/models/user.py` — read-only for validation
- `src/backend/models/project.py`
- `src/frontend/` — frontend changes in task 04/05

## Acceptance criteria
- [ ] Assign endpoint sets assignee_id on task
- [ ] Assign to invalid user returns 400
- [ ] Assign to inactive user returns 400
- [ ] Unassign endpoint clears assignee_id
- [ ] Unassign when no assignee returns 400
- [ ] Only admin/PM can assign/unassign
- [ ] My Tasks endpoint returns only tasks where current user is assignee
- [ ] My Tasks supports status and priority filters
- [ ] My Tasks returns stats summary (counts by status)
- [ ] Task counts by project returns correct numbers
- [ ] Audit logs written for assign/unassign actions
- [ ] `pytest tests/wave-4/test_task_assignments.py` passes
- [ ] `make lint` clean

## Test file
Create `tests/wave-4/test_task_assignments.py` with at least:
- `test_assign_task` — assign user, verify assignee_id and assignee_name in response
- `test_unassign_task` — assign then unassign, verify assignee_id is None
- `test_assign_invalid_user` — expect 400
- `test_assign_inactive_user` — expect 400
- `test_unassign_no_assignee` — expect 400
- `test_assign_unauthorized` — viewer role cannot assign, expect 403
- `test_my_tasks_returns_assigned_only` — create tasks, assign some to user, verify filtering
- `test_my_tasks_with_status_filter` — filter my tasks by status
- `test_my_tasks_with_priority_filter` — filter my tasks by priority
- `test_my_tasks_stats` — verify stats summary counts are correct
- `test_project_task_stats` — verify counts by status for a project
- `test_assign_audit_log` — verify audit entry with assignee info

## Notes
- Assignment is a privilege: only admin/PM can assign tasks
- My Tasks is a key UX feature — must be performant (use indexed query on assignee_id)
- User validation on assign prevents orphaned references
- Stats responses should be cacheable (add Cache-Control header in future)
- Notification system (email/Slack) is out of scope for this task — just log the assignment
