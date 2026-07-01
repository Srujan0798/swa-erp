# Task 02 — Task Status Transitions & Reorder

## Goal
Implement task status transition logic (state machine), bulk status update endpoint, drag-drop reorder (sort_order), and audit logging for all task mutations.

## Files to Create/Modify

### 1. Status Machine
Create `src/backend/core/task_workflow.py`:
```python
VALID_TRANSITIONS = {
    "todo": ["in_progress"],
    "in_progress": ["todo", "done"],
    "done": ["in_progress"],  # allow reopening
}
```
- `validate_transition(current_status: str, new_status: str) -> bool`
- `get_valid_transitions(current_status: str) -> list[str]`
- Raise `ValueError` on invalid transition with clear message

### 2. Reorder Logic
Add to `src/backend/db/repositories/task_repo.py`:
- `reorder_task(db, task_id, new_status: str, new_sort_order: int) -> Task` — move task to new column/position, update sort_order for affected tasks in that column
- `bulk_update_status(db, task_ids: list[uuid.UUID], new_status: str) -> int` — update status for multiple tasks, validate transition for each, write audit log

### 3. Schemas
Update `src/backend/schemas/task.py`:
- `TaskTransition` — to_status: TaskStatus (required)
- `TaskReorder` — status: TaskStatus, sort_order: int (required)
- `TaskBulkStatusUpdate` — task_ids: list[uuid.UUID], new_status: TaskStatus

### 4. Service Updates
Update `src/backend/services/task_service.py`:
- `transition_task_service(db, task_id, to_status, user_id)` → TaskRead
  1. Fetch current task
  2. Validate transition using task_workflow
  3. Update status
  4. Write audit log `task.transition` with old_status → new_status
  5. Return updated task
- `reorder_task_service(db, task_id, new_status, new_sort_order, user_id)` → TaskRead
  1. Validate transition
  2. Reorder within column
  3. Write audit log `task.reorder`
- `bulk_update_status_service(db, task_ids, new_status, user_id)` → int
  1. Validate each transition
  2. Update all
  3. Write single audit log `task.bulk_status` with affected task_ids

### 5. API Updates
Update `src/backend/api/tasks.py`:
- `POST /api/tasks/{task_id}/transition` — body: `TaskTransition`, returns updated task
- `POST /api/tasks/{task_id}/reorder` — body: `TaskReorder`, returns updated task
- `POST /api/tasks/bulk-status` — body: `TaskBulkStatusUpdate`, returns count of updated tasks

### 6. Audit Logging
Use existing `AuditLog` model from `src/backend/models/audit_log.py`:
- Log format: `action = "task.{action}"`, `entity_type = "task"`, `entity_id = task_id`, `metadata = {old_status, new_status, ...}`
- Ensure all transitions, updates, creates, deletes, comments are logged

## Files you must NOT touch
- `src/backend/models/audit_log.py` — use as-is
- `src/backend/api/projects.py`
- `src/frontend/` — frontend changes in task 04/05

## Acceptance criteria
- [ ] `validate_transition("todo", "in_progress")` returns True
- [ ] `validate_transition("todo", "done")` raises ValueError
- [ ] `validate_transition("done", "in_progress")` returns True (reopen allowed)
- [ ] Transition endpoint updates status and returns 200
- [ ] Invalid transition returns 400 with clear error message
- [ ] Reorder endpoint updates sort_order correctly
- [ ] Bulk status update processes multiple tasks atomically
- [ ] Bulk update validates each task's transition independently
- [ ] All transitions write audit log entries with correct metadata
- [ ] `pytest tests/wave-4/test_task_workflow.py` passes
- [ ] `make lint` clean

## Test file
Create `tests/wave-4/test_task_workflow.py` with at least:
- `test_valid_transition_todo_to_in_progress`
- `test_valid_transition_in_progress_to_done`
- `test_valid_transition_done_to_in_progress` (reopen)
- `test_invalid_transition_todo_to_done` — raises ValueError
- `test_invalid_transition_done_to_todo` — raises ValueError
- `test_transition_endpoint` — POST /api/tasks/{id}/transition, verify status changed
- `test_transition_invalid_returns_400`
- `test_reorder_within_column` — move task, verify sort_order updated
- `test_reorder_across_columns` — move from todo to in_progress column
- `test_bulk_status_update` — update 3 tasks, verify all changed
- `test_bulk_status_validates_individual_transitions` — one invalid task fails
- `test_audit_log_on_transition` — verify audit entry created
- `test_audit_log_metadata` — verify old_status and new_status in metadata

## Notes
- Transition validation is the critical business logic — thorough tests required
- sort_order should use integer spacing (e.g., 1000, 2000, 3000) to allow insertions without renumbering all tasks
- Reorder within same column: shift sort_orders of affected tasks
- Reorder across columns: validate transition first, then reorder in target column
- Audit log entries help with debugging and compliance
