import builtins
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from src.backend.models.task import Task, TaskComment, TaskDependency
from src.backend.schemas.task import TaskCreate, TaskFilter, TaskUpdate


class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: TaskCreate, reporter_id: UUID) -> Task:
        # TaskCreate has no `dependencies` field; dependencies are managed via
        # TaskDependencyRepository. Removing the previous (dead, attribute-error)
        # references that mypy flagged in wave-32.
        task = Task(**data.model_dump(), reporter_id=reporter_id)
        self.session.add(task)
        self.session.flush()
        return task

    def get(self, task_id: UUID) -> Task | None:
        stmt = (
            select(Task)
            .where(Task.id == task_id, Task.deleted_at.is_(None))
            .options(
                selectinload(Task.assignee),
                selectinload(Task.reporter),
                selectinload(Task.dependencies).selectinload(TaskDependency.depends_on_task),
                selectinload(Task.comments).selectinload(TaskComment.author),
            )
            .execution_options(populate_existing=True)
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def list(
        self, project_id: UUID | None, filters: TaskFilter, skip: int = 0, limit: int = 50
    ) -> list[Task]:
        stmt = (
            select(Task)
            .where(Task.deleted_at.is_(None))
            .options(
                selectinload(Task.assignee),
                selectinload(Task.reporter),
                selectinload(Task.comments),
            )
            .execution_options(populate_existing=True)
        )
        if project_id is not None:
            stmt = stmt.where(Task.project_id == project_id)
        if filters.status:
            stmt = stmt.where(Task.status == filters.status)
        if filters.assignee_id:
            stmt = stmt.where(Task.assignee_id == filters.assignee_id)
        if filters.due_before:
            stmt = stmt.where(Task.due_date <= filters.due_before)
        if filters.due_after:
            stmt = stmt.where(Task.due_date >= filters.due_after)
        if filters.search:
            stmt = stmt.where(Task.title.ilike(f"%{filters.search}%"))
        if filters.priority:
            _p = {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(filters.priority, None)
            if _p is not None:
                stmt = stmt.where(Task.priority == _p)
        stmt = stmt.order_by(Task.position, Task.created_at).offset(skip).limit(limit)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def update(self, task: Task, data: TaskUpdate) -> Task:
        for field, value in data.model_dump(exclude_unset=True).items():
            if field != "version":
                setattr(task, field, value)
        task.version = (task.version or 0) + 1
        task.updated_at = datetime.now(tz=UTC)
        self.session.flush()
        return task

    def delete(self, task: Task) -> None:
        self.session.delete(task)
        self.session.flush()

    def count_by_project(self, project_id: UUID) -> int:
        stmt = select(func.count(Task.id)).where(
            Task.project_id == project_id, Task.deleted_at.is_(None)
        )
        result = self.session.execute(stmt)
        return result.scalar_one()

    def count_by_user(self, user_id: UUID) -> dict:
        todo = select(func.count(Task.id)).where(
            Task.assignee_id == user_id, Task.status == "todo", Task.deleted_at.is_(None)
        )
        in_progress = select(func.count(Task.id)).where(
            Task.assignee_id == user_id, Task.status == "in_progress", Task.deleted_at.is_(None)
        )
        done = select(func.count(Task.id)).where(
            Task.assignee_id == user_id, Task.status == "done", Task.deleted_at.is_(None)
        )
        total = select(func.count(Task.id)).where(
            Task.assignee_id == user_id, Task.deleted_at.is_(None)
        )
        return {
            "todo": self.session.execute(todo).scalar_one(),
            "in_progress": self.session.execute(in_progress).scalar_one(),
            "done": self.session.execute(done).scalar_one(),
            "total": self.session.execute(total).scalar_one(),
        }

    def get_blocked_tasks(self, task_id: UUID) -> builtins.list[UUID]:
        """Return all task IDs that depend (directly or transitively) on task_id."""
        stmt = text(
            """
        WITH RECURSIVE deps AS (
            SELECT task_id, depends_on_task_id FROM task_dependencies WHERE depends_on_task_id = :tid
            UNION ALL
            SELECT td.task_id, td.depends_on_task_id
            FROM task_dependencies td
            JOIN deps d ON td.depends_on_task_id = d.task_id
        )
        SELECT task_id FROM deps
        """
        )
        result = self.session.execute(stmt, {"tid": task_id})
        return [row[0] for row in result.fetchall()]


_repo = TaskRepository.__dict__


_priority_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def create_task(
    db: Session,
    *,
    project_id: UUID,
    title: str,
    reporter_id: UUID,
    description: str | None = None,
    priority: str = "medium",
    assignee_id: UUID | None = None,
    due_date=None,
) -> Task:
    priority_int = _priority_map.get(priority, 2)
    task = Task(
        project_id=project_id,
        title=title,
        description=description,
        status="todo",
        priority=priority_int,
        assignee_id=assignee_id,
        due_date=due_date,
        reporter_id=reporter_id,
    )
    db.add(task)
    db.flush()
    return task


def get_task_with_names(db: Session, task_id: UUID) -> dict | None:
    repo = TaskRepository(db)
    task = repo.get(task_id)
    if not task:
        return None
    assignee_name = task.assignee.name if getattr(task, "assignee", None) else None
    creator_name = task.reporter.name if getattr(task, "reporter", None) else None
    comment_count = len(getattr(task, "comments", []) or [])
    return {
        "task": task,
        "assignee_name": assignee_name,
        "creator_name": creator_name,
        "comment_count": comment_count,
    }


def list_by_project(
    db: Session,
    project_id: UUID,
    page: int,
    page_size: int,
    status: str | None,
    assignee_id: UUID | None,
    priority: str | None,
) -> tuple:
    repo = TaskRepository(db)
    filters = TaskFilter(status=status, assignee_id=assignee_id, priority=priority)
    skip = (page - 1) * page_size
    items = repo.list(project_id, filters, skip=skip, limit=page_size)
    total = repo.count_by_project(project_id)
    return items, total


def list_tasks_by_assignee(
    db: Session, user_id: UUID, page: int, page_size: int, status: str | None, priority: str | None
) -> tuple:
    repo = TaskRepository(db)
    filters = TaskFilter(status=status, assignee_id=user_id, priority=priority)
    skip = (page - 1) * page_size
    items = repo.list(None, filters, skip=skip, limit=page_size)
    total = repo.count_by_user(user_id)["total"]
    return items, total


def get_by_id(db: Session, task_id: UUID) -> Task | None:
    repo = TaskRepository(db)
    return repo.get(task_id)


def get_user_by_id(db: Session, user_id: UUID):
    # Callers need User for assignment; exclude soft-deleted accounts.
    from src.backend.models.user import User

    return db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()


def update_task(db: Session, task: Task, **kwargs) -> Task:
    repo = TaskRepository(db)
    existing = repo.get(task.id)
    if not existing:
        raise ValueError("Task not found")
    update_data = TaskUpdate(**{k: v for k, v in kwargs.items() if k in TaskUpdate.model_fields})
    return repo.update(existing, update_data)


def assign_task(db: Session, task_id: UUID, assignee_id: UUID) -> Task | None:
    repo = TaskRepository(db)
    task = repo.get(task_id)
    if not task:
        return None
    task.assignee_id = assignee_id
    repo.session.flush()
    repo.session.refresh(task, ["assignee"])
    return task


def unassign_task(db: Session, task_id: UUID) -> Task | None:
    repo = TaskRepository(db)
    task = repo.get(task_id)
    if not task:
        return None
    task.assignee_id = None
    repo.session.flush()
    repo.session.refresh(task, ["assignee"])
    return task


def bulk_update_status(db: Session, task_ids: list[UUID], new_status: str) -> int:
    stmt = select(Task).where(Task.id.in_(task_ids), Task.deleted_at.is_(None))
    result = db.execute(stmt)
    tasks = result.scalars().all()
    count = 0
    for task in tasks:
        if task.status != new_status:
            task.status = new_status
            count += 1
    if count:
        db.flush()
    return count


def reorder_task(db: Session, task_id: UUID, new_status: str, new_sort_order: int) -> Task | None:
    repo = TaskRepository(db)
    task = repo.get(task_id)
    if not task:
        return None
    task.status = new_status
    task.position = new_sort_order
    db.flush()
    return task


def soft_delete(db: Session, task_id: UUID) -> bool:
    repo = TaskRepository(db)
    task = repo.get(task_id)
    if not task:
        return False
    task.deleted_at = datetime.now(tz=UTC)
    db.flush()
    return True


def create_comment(db: Session, task_id: UUID, author_id: UUID, content: str) -> TaskComment:
    comment = TaskComment(task_id=task_id, author_id=author_id, content=content)
    db.add(comment)
    db.flush()
    return comment


def list_comments(db: Session, task_id: UUID) -> list[TaskComment]:
    stmt = (
        select(TaskComment)
        .where(TaskComment.task_id == task_id)
        .order_by(TaskComment.created_at.asc())
    )
    result = db.execute(stmt)
    return list(result.scalars().all())


def get_task_counts_by_project(db: Session, project_id: UUID) -> dict:
    repo = TaskRepository(db)
    total = repo.count_by_project(project_id)
    todo = select(func.count(Task.id)).where(
        Task.project_id == project_id, Task.status == "todo", Task.deleted_at.is_(None)
    )
    in_progress = select(func.count(Task.id)).where(
        Task.project_id == project_id, Task.status == "in_progress", Task.deleted_at.is_(None)
    )
    done_count = select(func.count(Task.id)).where(
        Task.project_id == project_id, Task.status == "done", Task.deleted_at.is_(None)
    )
    return {
        "todo": db.execute(todo).scalar_one(),
        "in_progress": db.execute(in_progress).scalar_one(),
        "done": db.execute(done_count).scalar_one(),
        "total": total,
    }


def get_task_counts_by_user(db: Session, user_id: UUID) -> dict:
    repo = TaskRepository(db)
    return repo.count_by_user(user_id)
