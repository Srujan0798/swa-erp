import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.backend.models.task import Task, TaskComment
from src.backend.models.user import User


def create_task(
    db: Session,
    project_id: uuid.UUID,
    title: str,
    created_by: uuid.UUID,
    description: str | None = None,
    priority: str = "medium",
    assignee_id: uuid.UUID | None = None,
    due_date=None,
) -> Task:
    task = Task(
        project_id=project_id,
        title=title,
        description=description,
        priority=priority,
        assignee_id=assignee_id,
        due_date=due_date,
        created_by=created_by,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_by_id(db: Session, task_id: uuid.UUID) -> Task | None:
    return db.query(Task).filter(Task.id == task_id, Task.deleted_at.is_(None)).first()


def get_task_with_names(db: Session, task_id: uuid.UUID) -> dict | None:
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.deleted_at.is_(None))
        .first()
    )
    if not task:
        return None

    assignee_name = None
    creator_name = None
    comment_count = 0

    if task.assignee_id:
        user = db.query(User).filter(User.id == task.assignee_id).first()
        assignee_name = user.name if user else None

    creator = db.query(User).filter(User.id == task.created_by).first()
    creator_name = creator.name if creator else None

    comment_count = db.query(func.count(TaskComment.id)).filter(
        TaskComment.task_id == task.id
    ).scalar()

    return {
        "task": task,
        "assignee_name": assignee_name,
        "creator_name": creator_name,
        "comment_count": comment_count,
    }


def _list_query(db: Session, filters: list | None = None):
    query = db.query(Task).filter(Task.deleted_at.is_(None))
    if filters:
        for f in filters:
            query = query.filter(f)
    return query


def list_by_project(
    db: Session,
    project_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    assignee_id: uuid.UUID | None = None,
    priority: str | None = None,
) -> tuple[list[dict], int]:
    filters = [Task.project_id == project_id]
    if status:
        filters.append(Task.status == status)
    if assignee_id:
        filters.append(Task.assignee_id == assignee_id)
    if priority:
        filters.append(Task.priority == priority)

    query = _list_query(db, filters)
    total = query.count()
    offset = (page - 1) * page_size
    tasks = query.order_by(Task.sort_order.asc(), Task.created_at.desc()).offset(offset).limit(page_size).all()

    items = []
    for task in tasks:
        data = _task_to_dict(db, task)
        items.append(data)

    return items, total


def _task_to_dict(db: Session, task: Task) -> dict:
    assignee_name = None
    creator_name = None

    if task.assignee_id:
        user = db.query(User).filter(User.id == task.assignee_id).first()
        assignee_name = user.name if user else None

    creator = db.query(User).filter(User.id == task.created_by).first()
    creator_name = creator.name if creator else None

    comment_count = db.query(func.count(TaskComment.id)).filter(
        TaskComment.task_id == task.id
    ).scalar()

    return {
        "id": task.id,
        "project_id": task.project_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "assignee_id": task.assignee_id,
        "assignee_name": assignee_name,
        "created_by": task.created_by,
        "created_by_name": creator_name,
        "due_date": task.due_date,
        "sort_order": task.sort_order,
        "comment_count": comment_count,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


def update_task(db: Session, task: Task, **fields) -> Task:
    for key, value in fields.items():
        if hasattr(task, key):
            setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


def soft_delete(db: Session, task_id: uuid.UUID) -> bool:
    task = db.query(Task).filter(Task.id == task_id, Task.deleted_at.is_(None)).first()
    if not task:
        return False
    task.deleted_at = datetime.utcnow()
    db.commit()
    return True


def get_task_counts_by_project(db: Session, project_id: uuid.UUID) -> dict:
    base = db.query(func.count(Task.id)).filter(
        Task.project_id == project_id,
        Task.deleted_at.is_(None),
    )
    todo = base.filter(Task.status == "todo").scalar() or 0
    in_progress = base.filter(Task.status == "in_progress").scalar() or 0
    done = base.filter(Task.status == "done").scalar() or 0
    total = todo + in_progress + done
    return {"todo": todo, "in_progress": in_progress, "done": done, "total": total}


def create_comment(db: Session, task_id: uuid.UUID, user_id: uuid.UUID, content: str) -> TaskComment:
    comment = TaskComment(task_id=task_id, user_id=user_id, content=content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_comments(db: Session, task_id: uuid.UUID) -> list[dict]:
    comments = (
        db.query(TaskComment)
        .filter(TaskComment.task_id == task_id)
        .order_by(TaskComment.created_at.asc())
        .all()
    )
    items = []
    for c in comments:
        user = db.query(User).filter(User.id == c.user_id).first()
        items.append({
            "id": c.id,
            "task_id": c.task_id,
            "user_id": c.user_id,
            "user_name": user.name if user else None,
            "content": c.content,
            "created_at": c.created_at,
        })
    return items


# --- Task 02: Reorder / Bulk Status ---


def reorder_task(db: Session, task_id: uuid.UUID, new_status: str, new_sort_order: int) -> Task | None:
    task = db.query(Task).filter(Task.id == task_id, Task.deleted_at.is_(None)).first()
    if not task:
        return None
    task.status = new_status
    task.sort_order = new_sort_order
    db.commit()
    db.refresh(task)
    return task


def bulk_update_status(db: Session, task_ids: list[uuid.UUID], new_status: str) -> int:
    count = (
        db.query(Task)
        .filter(Task.id.in_(task_ids), Task.deleted_at.is_(None))
        .update({Task.status: new_status}, synchronize_session="fetch")
    )
    db.commit()
    return count


# --- Task 03: Assignment ---


def assign_task(db: Session, task_id: uuid.UUID, assignee_id: uuid.UUID) -> Task | None:
    task = db.query(Task).filter(Task.id == task_id, Task.deleted_at.is_(None)).first()
    if not task:
        return None
    task.assignee_id = assignee_id
    db.commit()
    db.refresh(task)
    return task


def unassign_task(db: Session, task_id: uuid.UUID) -> Task | None:
    task = db.query(Task).filter(Task.id == task_id, Task.deleted_at.is_(None)).first()
    if not task:
        return None
    task.assignee_id = None
    db.commit()
    db.refresh(task)
    return task


def list_tasks_by_assignee(
    db: Session,
    user_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    priority: str | None = None,
) -> tuple[list[dict], int]:
    filters = [Task.assignee_id == user_id]
    if status:
        filters.append(Task.status == status)
    if priority:
        filters.append(Task.priority == priority)

    query = _list_query(db, filters)
    total = query.count()
    offset = (page - 1) * page_size
    tasks = query.order_by(Task.created_at.desc()).offset(offset).limit(page_size).all()

    items = [_task_to_dict(db, t) for t in tasks]
    return items, total


def get_task_counts_by_user(db: Session, user_id: uuid.UUID) -> dict:
    base = db.query(func.count(Task.id)).filter(
        Task.assignee_id == user_id,
        Task.deleted_at.is_(None),
    )
    todo = base.filter(Task.status == "todo").scalar() or 0
    in_progress = base.filter(Task.status == "in_progress").scalar() or 0
    done = base.filter(Task.status == "done").scalar() or 0
    total = todo + in_progress + done
    return {"todo": todo, "in_progress": in_progress, "done": done, "total": total}


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.query(User).filter(User.id == user_id, User.is_active.is_(True), User.deleted_at.is_(None)).first()
