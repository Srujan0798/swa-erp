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
    TaskUpdate,
)
from src.backend.services.task_service import (
    add_comment_service,
    assign_task_service,
    bulk_update_status_service,
    create_task_service,
    delete_task_service,
    get_task_counts_service,
    get_task_service,
    list_my_tasks_service,
    list_tasks_service,
    transition_task_service,
    reorder_task_service,
    unassign_task_service,
    update_task_service,
)

router = APIRouter(tags=["tasks"])


# --- Task 01: CRUD ---


@router.post(
    "/api/projects/{project_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task_endpoint(
    project_id: uuid.UUID,
    body: TaskCreate,
    current_user: User = Depends(require_role(Role.PM)),
    db: Session = Depends(get_db),
) -> TaskRead:
    return create_task_service(db, project_id, body, current_user.id)


@router.get("/api/projects/{project_id}/tasks", response_model=TaskListResponse)
def list_tasks_endpoint(
    project_id: uuid.UUID,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskStatsResponse:
    return get_task_counts_service(db, project_id)


@router.get("/api/tasks/{task_id}", response_model=TaskRead)
def get_task_endpoint(
    task_id: uuid.UUID,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskRead:
    task = get_task_service(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/api/tasks/{task_id}", response_model=TaskRead)
def update_task_endpoint(
    task_id: uuid.UUID,
    body: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskRead:
    task = update_task_service(db, task_id, body, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_endpoint(
    task_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),
    db: Session = Depends(get_db),
) -> None:
    success = delete_task_service(db, task_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")


@router.post("/api/tasks/{task_id}/comments", response_model=TaskCommentRead, status_code=status.HTTP_201_CREATED)
def add_comment_endpoint(
    task_id: uuid.UUID,
    body: TaskCommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskCommentRead:
    comment = add_comment_service(db, task_id, current_user.id, body.content)
    if not comment:
        raise HTTPException(status_code=404, detail="Task not found")
    return comment


@router.get("/api/tasks/{task_id}/comments", response_model=list[TaskCommentRead])
def list_comments_endpoint(
    task_id: uuid.UUID,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TaskCommentRead]:
    from src.backend.db.repositories.task_repo import list_comments

    items = list_comments(db, task_id)
    return [TaskCommentRead(**item) for item in items]


# --- Task 02: Transitions ---


@router.post("/api/tasks/{task_id}/transition", response_model=TaskRead)
def transition_task_endpoint(
    task_id: uuid.UUID,
    body: TaskTransition,
    current_user: User = Depends(require_role(Role.PM)),
    db: Session = Depends(get_db),
) -> TaskRead:
    task = transition_task_service(db, task_id, body.to_status.value, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/api/tasks/{task_id}/reorder", response_model=TaskRead)
def reorder_task_endpoint(
    task_id: uuid.UUID,
    body: TaskReorder,
    current_user: User = Depends(require_role(Role.PM)),
    db: Session = Depends(get_db),
) -> TaskRead:
    task = reorder_task_service(
        db, task_id, body.status.value, body.sort_order, current_user.id
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/api/tasks/bulk-status")
def bulk_status_endpoint(
    body: TaskBulkStatusUpdate,
    current_user: User = Depends(require_role(Role.PM)),
    db: Session = Depends(get_db),
) -> dict:
    count = bulk_update_status_service(
        db, body.task_ids, body.new_status.value, current_user.id
    )
    return {"updated": count}


# --- Task 03: Assignment ---


@router.post("/api/tasks/{task_id}/assign", response_model=TaskRead)
def assign_task_endpoint(
    task_id: uuid.UUID,
    body: TaskAssign,
    current_user: User = Depends(require_role(Role.PM)),
    db: Session = Depends(get_db),
) -> TaskRead:
    task = assign_task_service(db, task_id, body.assignee_id, current_user.id)
    if task is None:
        raise HTTPException(
            status_code=400,
            detail="Task not found or assignee is invalid/inactive",
        )
    return task


@router.delete("/api/tasks/{task_id}/assign", response_model=TaskRead)
def unassign_task_endpoint(
    task_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),
    db: Session = Depends(get_db),
) -> TaskRead:
    task = unassign_task_service(db, task_id, current_user.id)
    if task is None:
        raise HTTPException(
            status_code=400,
            detail="Task not found or task has no assignee",
        )
    return task


@router.get("/api/tasks/my-tasks", response_model=MyTasksResponse)
def my_tasks_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = None,
    priority: str | None = None,
) -> MyTasksResponse:
    return list_my_tasks_service(db, current_user.id, page, page_size, status, priority)
