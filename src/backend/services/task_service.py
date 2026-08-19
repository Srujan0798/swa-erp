import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.backend.core.task_workflow import validate_transition
from src.backend.db.repositories.audit_repo import create_entry
from src.backend.db.repositories.task_repo import (
    assign_task,
    bulk_update_status,
    create_comment,
    create_task,
    get_by_id,
    get_task_counts_by_project,
    get_task_counts_by_user,
    get_task_with_names,
    get_user_by_id,
    list_by_project,
    list_tasks_by_assignee,
    reorder_task,
    soft_delete,
    unassign_task,
    update_task,
)
from src.backend.schemas.task import (
    MyTasksResponse,
    TaskCommentRead,
    TaskCreate,
    TaskRead,
    TaskStatsResponse,
    TaskUpdate,
)


def _task_read(db: Session, task) -> TaskRead:
    data = get_task_with_names(db, task.id)
    if not data:
        return TaskRead.model_validate(task)
    t = data["task"]
    return TaskRead(
        id=t.id,
        project_id=t.project_id,
        title=t.title,
        description=t.description,
        status=t.status,
        priority=t.priority,
        assignee_id=t.assignee_id,
        assignee_name=data["assignee_name"],
        created_by=t.reporter_id,
        created_by_name=data["creator_name"],
        due_date=t.due_date,
        sort_order=t.position,
        comment_count=data["comment_count"],
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


def create_task_service(
    db: Session,
    project_id: uuid.UUID,
    body: TaskCreate,
    created_by: uuid.UUID,
) -> TaskRead:
    if body.assignee_id is not None:
        assignee = get_user_by_id(db, body.assignee_id)
        if not assignee or not getattr(assignee, "is_active", True):
            raise HTTPException(status_code=400, detail="Assignee not found or inactive")
    task = create_task(
        db,
        project_id=project_id,
        title=body.title,
        reporter_id=created_by,
        description=body.description,
        priority=body.priority.value if body.priority else "medium",
        assignee_id=body.assignee_id,
        due_date=body.due_date,
    )
    create_entry(
        db,
        action="task.create",
        entity_type="task",
        user_id=created_by,
        entity_id=task.id,
        after_json={"title": task.title, "project_id": str(project_id)},
    )
    return _task_read(db, task)


def get_task_service(db: Session, task_id: uuid.UUID) -> TaskRead | None:
    data = get_task_with_names(db, task_id)
    if not data:
        return None
    t = data["task"]
    return TaskRead(
        id=t.id,
        project_id=t.project_id,
        title=t.title,
        description=t.description,
        status=t.status,
        priority=t.priority,
        assignee_id=t.assignee_id,
        assignee_name=data["assignee_name"],
        created_by=t.reporter_id,
        created_by_name=data["creator_name"],
        due_date=t.due_date,
        sort_order=t.position,
        comment_count=data["comment_count"],
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


def list_tasks_service(
    db: Session,
    project_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    assignee_id: uuid.UUID | None = None,
    priority: str | None = None,
) -> tuple[list[TaskRead], int, int, int]:
    items, total = list_by_project(db, project_id, page, page_size, status, assignee_id, priority)
    reads = [_task_read(db, item) for item in items]
    return reads, total, page, page_size


def list_my_tasks_service(
    db: Session,
    user_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    priority: str | None = None,
) -> MyTasksResponse:
    items, total = list_tasks_by_assignee(db, user_id, page, page_size, status, priority)
    reads = [_task_read(db, item) for item in items]
    stats_data = get_task_counts_by_user(db, user_id)
    stats = TaskStatsResponse(**stats_data)
    return MyTasksResponse(items=reads, total=total, stats=stats)


def update_task_service(
    db: Session,
    task_id: uuid.UUID,
    body: TaskUpdate,
    user_id: uuid.UUID,
) -> TaskRead | None:
    task = get_by_id(db, task_id)
    if not task:
        return None

    update_fields = body.model_dump(exclude_unset=True)
    if "priority" in update_fields and update_fields["priority"] is not None:
        update_fields["priority"] = update_fields["priority"].value

    task = update_task(db, task, **update_fields)

    create_entry(
        db,
        action="task.update",
        entity_type="task",
        user_id=user_id,
        entity_id=task_id,
        after_json=update_fields,
    )

    return _task_read(db, task)


def delete_task_service(db: Session, task_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    task = get_by_id(db, task_id)
    if not task:
        return False

    success = soft_delete(db, task_id)
    if success:
        create_entry(
            db,
            action="task.delete",
            entity_type="task",
            user_id=user_id,
            entity_id=task_id,
        )
    return success


def add_comment_service(
    db: Session,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    content: str,
) -> TaskCommentRead | None:
    task = get_by_id(db, task_id)
    if not task:
        return None

    comment = create_comment(db, task_id, user_id, content)

    create_entry(
        db,
        action="task.comment",
        entity_type="task",
        user_id=user_id,
        entity_id=task_id,
    )

    from src.backend.models.user import User

    user = db.query(User).filter(User.id == user_id).first()
    return TaskCommentRead(
        id=comment.id,
        task_id=comment.task_id,
        user_id=comment.author_id,
        user_name=user.name if user else None,
        content=comment.content,
        created_at=comment.created_at,
    )


def get_task_counts_service(db: Session, project_id: uuid.UUID) -> dict:
    return get_task_counts_by_project(db, project_id)


# --- Task 02: Transitions ---


def transition_task_service(
    db: Session,
    task_id: uuid.UUID,
    to_status: str,
    user_id: uuid.UUID,
) -> TaskRead | None:
    task = get_by_id(db, task_id)
    if not task:
        return None

    old_status = task.status
    validate_transition(old_status, to_status)

    task.status = to_status
    db.flush()

    create_entry(
        db,
        action="task.transition",
        entity_type="task",
        user_id=user_id,
        entity_id=task_id,
        before_json={"old_status": old_status},
        after_json={"new_status": to_status},
    )
    db.commit()

    return _task_read(db, task)


def reorder_task_service(
    db: Session,
    task_id: uuid.UUID,
    new_status: str,
    new_sort_order: int,
    user_id: uuid.UUID,
) -> TaskRead | None:
    task = get_by_id(db, task_id)
    if not task:
        return None

    validate_transition(task.status, new_status)

    task = reorder_task(db, task_id, new_status, new_sort_order)
    if not task:
        return None

    create_entry(
        db,
        action="task.reorder",
        entity_type="task",
        user_id=user_id,
        entity_id=task_id,
        after_json={"new_status": new_status, "new_sort_order": new_sort_order},
    )

    return _task_read(db, task)


def bulk_update_status_service(
    db: Session,
    task_ids: list[uuid.UUID],
    new_status: str,
    user_id: uuid.UUID,
) -> int:
    for tid in task_ids:
        task = get_by_id(db, tid)
        if task:
            validate_transition(task.status, new_status)

    count = bulk_update_status(db, task_ids, new_status)

    create_entry(
        db,
        action="task.bulk_status",
        entity_type="task",
        user_id=user_id,
        after_json={"task_ids": [str(t) for t in task_ids], "new_status": new_status},
    )

    return count


# --- Task 03: Assignment ---


def assign_task_service(
    db: Session,
    task_id: uuid.UUID,
    assignee_id: uuid.UUID,
    user_id: uuid.UUID,
) -> TaskRead | None:
    task = get_by_id(db, task_id)
    if not task:
        return None

    assignee = get_user_by_id(db, assignee_id)
    if not assignee:
        return None

    updated = assign_task(db, task_id, assignee_id)
    if not updated:
        return None

    create_entry(
        db,
        action="task.assign",
        entity_type="task",
        user_id=user_id,
        entity_id=task_id,
        after_json={
            "assignee_id": str(assignee_id),
            "assignee_name": assignee.name,
        },
    )

    return _task_read(db, updated)


def unassign_task_service(
    db: Session,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
) -> TaskRead | None:
    task = get_by_id(db, task_id)
    if not task:
        return None

    if not task.assignee_id:
        return None

    updated = unassign_task(db, task_id)
    if not updated:
        return None

    create_entry(
        db,
        action="task.unassign",
        entity_type="task",
        user_id=user_id,
        entity_id=task_id,
    )

    return _task_read(db, updated)


def get_project_task_stats_service(db: Session, project_id: uuid.UUID) -> TaskStatsResponse:
    data = get_task_counts_by_project(db, project_id)
    return TaskStatsResponse(**data)
