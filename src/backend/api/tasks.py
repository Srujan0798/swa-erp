import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.task import (
    MyTasksResponse,
    TaskAssign,
    TaskAssignResponse,
    TaskBulkStatusUpdate,
    TaskCommentCreate,
    TaskCommentRead,
    TaskCreate,
    TaskListResponse,
    TaskRead,
    TaskReorder,
    TaskStatsResponse,
    TaskTransition,
)
from src.backend.services.task_service import (
    add_comment_service,
    assign_task_service,
    bulk_update_status_service,
    create_task_service,
    get_task_counts_service,
    get_task_service,
    list_my_tasks_service,
    list_tasks_service,
    reorder_task_service,
    transition_task_service,
    unassign_task_service,
)

router = APIRouter(tags=["tasks"])


@router.post(
    "/api/projects/{project_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task_endpoint(
    project_id: uuid.UUID,
    body: TaskCreate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TaskRead:
    return create_task_service(db, project_id, body, current_user.id)


@router.get("/api/projects/{project_id}/tasks", response_model=TaskListResponse)
def list_tasks_endpoint(
    project_id: uuid.UUID,
    _: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = None,
    assignee_id: uuid.UUID | None = None,
    priority: str | None = None,
) -> TaskListResponse:
    items, total, p, ps = list_tasks_service(
        db, project_id, page, page_size, status, assignee_id, priority
    )
    return TaskListResponse(items=items, total=total, page=p, page_size=ps)


@router.get("/api/projects/{project_id}/tasks/stats", response_model=TaskStatsResponse)
def task_stats_endpoint(
    project_id: uuid.UUID,
    _: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TaskStatsResponse:
    return get_task_counts_service(db, project_id)


# IMPORTANT: /api/tasks/my-tasks MUST be defined BEFORE /api/tasks/{task_id}
# FastAPI matches routes in order; otherwise "my-tasks" matches as a task_id UUID
@router.get("/api/tasks/my-tasks")
def my_tasks_endpoint(
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = None,
    priority: str | None = None,
) -> MyTasksResponse:
    return list_my_tasks_service(db, current_user.id, page, page_size, status, priority)


@router.post("/api/tasks/bulk-status", response_model=int)
def bulk_update_status_endpoint(
    body: TaskBulkStatusUpdate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> int:
    count = bulk_update_status_service(db, body.task_ids, body.new_status, current_user.id)
    return count


@router.get("/api/tasks/{task_id}", response_model=TaskRead)
def get_task_endpoint(
    task_id: uuid.UUID,
    _: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TaskRead:
    task = get_task_service(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/api/tasks/{task_id}/transition", response_model=TaskRead)
def transition_task_endpoint(
    task_id: uuid.UUID,
    body: TaskTransition,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TaskRead:
    task = transition_task_service(db, task_id, body.to_status, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or invalid transition")
    return task


@router.post("/api/tasks/{task_id}/reorder", response_model=TaskRead)
def reorder_task_endpoint(
    task_id: uuid.UUID,
    body: TaskReorder,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TaskRead:
    task = reorder_task_service(db, task_id, body.status, body.sort_order, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or invalid transition")
    return task


@router.post("/api/tasks/{task_id}/assign", response_model=TaskAssignResponse)
def assign_task_endpoint(
    task_id: uuid.UUID,
    body: TaskAssign,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TaskAssignResponse:
    task = get_task_service(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    assignee = (
        db.query(User)
        .filter(
            User.id == body.assignee_id,
            User.is_active.is_(True),
            User.deleted_at.is_(None),
        )
        .first()
    )
    if not assignee:
        raise HTTPException(status_code=400, detail="Assignee not found or inactive")
    result = assign_task_service(db, task_id, body.assignee_id, current_user.id)
    if not result:
        raise HTTPException(status_code=400, detail="Could not assign task")
    return TaskAssignResponse(
        task_id=result.id,
        assignee_id=result.assignee_id,
        assignee_name=result.assignee_name,
    )


@router.delete("/api/tasks/{task_id}/assign", response_model=TaskRead)
def unassign_task_endpoint(
    task_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TaskRead:
    task = get_task_service(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.assignee_id:
        raise HTTPException(status_code=400, detail="Task is not assigned to anyone")
    result = unassign_task_service(db, task_id, current_user.id)
    if not result:
        raise HTTPException(status_code=400, detail="Could not unassign task")
    return result


@router.post("/api/tasks/{task_id}/comments", response_model=TaskCommentRead)
def add_comment_endpoint(
    task_id: uuid.UUID,
    body: TaskCommentCreate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TaskCommentRead:
    comment = add_comment_service(db, task_id, current_user.id, body.content)
    if not comment:
        raise HTTPException(status_code=404, detail="Task not found")
    return comment
