# Wave-4 Task 1: Task Models & CRUD API

**Skill:** `tdd`, `code-review`, `fastapi-crud`, `sqlalchemy-models`
**Estimated:** 45 min

---

## Goal
Implement SQLAlchemy models, repositories, and FastAPI CRUD endpoints for tasks.

---

## Files to Create/Modify

### 1. SQLAlchemy Models (`src/backend/models/task.py`)
```python
from sqlalchemy import (
    Column, String, Text, Integer, ForeignKey, DateTime,
    DECIMAL, Index, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.backend.models.base import Base
import uuid
from datetime import datetime

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="todo", index=True)
    priority = Column(Integer, default=0)
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    estimated_hours = Column(DECIMAL(6,2), nullable=True)
    actual_hours = Column(DECIMAL(6,2), default=0)
    position = Column(Integer, default=0)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reported_tasks")
    dependencies = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.task_id",
        back_populates="task",
        cascade="all, delete-orphan"
    )
    dependents = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.depends_on_task_id",
        back_populates="depends_on_task",
        cascade="all, delete-orphan"
    )
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_tasks_project_status", "project_id", "status"),
        Index("ix_tasks_assignee_status", "assignee_id", "status"),
    )


class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    depends_on_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    task = relationship("Task", foreign_keys=[task_id], back_populates="dependencies")
    depends_on_task = relationship("Task", foreign_keys=[depends_on_task_id], back_populates="dependents")


class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey("task_comments.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="task_comments")
    parent = relationship("TaskComment", remote_side=[id], back_populates="replies")
    replies = relationship("TaskComment", back_populates="parent")
```

### 2. Repository (`src/backend/db/repositories/task_repo.py`)
```python
from uuid import UUID
from typing import List, Optional
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.backend.models.task import Task, TaskDependency, TaskComment
from src.backend.schemas.task import TaskCreate, TaskUpdate, TaskFilter

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: TaskCreate, reporter_id: UUID) -> Task:
        task = Task(**data.model_dump(exclude={"dependencies"}), reporter_id=reporter_id)
        self.session.add(task)
        await self.session.flush()
        if data.dependencies:
            for dep_id in data.dependencies:
                dep = TaskDependency(task_id=task.id, depends_on_task_id=dep_id)
                self.session.add(dep)
        await self.session.flush()
        return task

    async def get(self, task_id: UUID) -> Optional[Task]:
        stmt = select(Task).where(Task.id == task_id).options(
            selectinload(Task.assignee),
            selectinload(Task.reporter),
            selectinload(Task.dependencies).selectinload(TaskDependency.depends_on_task),
            selectinload(Task.comments).selectinload(TaskComment.author)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, project_id: UUID, filters: TaskFilter, skip: int = 0, limit: int = 50) -> List[Task]:
        stmt = select(Task).where(Task.project_id == project_id)
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
        stmt = stmt.order_by(Task.position, Task.created_at).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, task: Task, data: TaskUpdate) -> Task:
        for field, value in data.model_dump(exclude_unset=True).items():
            if field != "version":
                setattr(task, field, value)
        task.version += 1
        task.updated_at = func.now()
        await self.session.flush()
        return task

    async def delete(self, task: Task) -> None:
        await self.session.delete(task)
        await self.session.flush()

    async def count_by_project(self, project_id: UUID) -> int:
        stmt = select(func.count(Task.id)).where(Task.project_id == project_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_blocked_tasks(self, task_id: UUID) -> List[UUID]:
        """Return all task IDs that depend (directly or transitively) on task_id."""
        # Recursive CTE for transitive closure
        stmt = """
        WITH RECURSIVE deps AS (
            SELECT task_id, depends_on_task_id FROM task_dependencies WHERE depends_on_task_id = :tid
            UNION ALL
            SELECT td.task_id, td.depends_on_task_id
            FROM task_dependencies td
            JOIN deps d ON td.depends_on_task_id = d.task_id
        )
        SELECT task_id FROM deps
        """
        result = await self.session.execute(text(stmt), {"task_id": task_id})
        return [row[0] for row in result.fetchall()]
```

### 3. Schemas (`src/backend/schemas/task.py`)
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

class TaskPriority(int, Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    URGENT = 3

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: int = 0
    assignee_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    dependencies: List[UUID] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None
    assignee_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    version: int = Field(..., ge=1)  # Optimistic lock

class TaskFilter(BaseModel):
    status: Optional[str] = None
    assignee_id: Optional[UUID] = None
    due_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    search: Optional[str] = None

class TaskRead(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    description: Optional[str]
    status: str
    priority: int
    assignee_id: Optional[UUID]
    assignee_name: Optional[str] = None
    reporter_id: UUID
    due_date: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_hours: Optional[float]
    actual_hours: float
    position: int
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskDependencyRead(BaseModel):
    task_id: UUID
    depends_on_task_id: UUID
    depends_on_task_title: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TaskCommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    parent_comment_id: Optional[UUID] = None

class TaskCommentRead(BaseModel):
    id: UUID
    task_id: UUID
    author_id: UUID
    author_name: Optional[str] = None
    parent_comment_id: Optional[UUID]
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    replies_count: int = 0

    class Config:
        from_attributes = True
```

### 4. Service (`src/backend/services/task_service.py`)
```python
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.db.repositories.task_repo import TaskRepository
from src.backend.schemas.task import TaskCreate, TaskUpdate, TaskFilter
from src.backend.core.exceptions import NotFoundError, ConflictError, ForbiddenError

class TaskService:
    def __init__(self, session: AsyncSession):
        self.repo = TaskRepository(session)

    async def create(self, data: TaskCreate, reporter_id: UUID, current_user_id: UUID) -> Task:
        # Verify project access (PM/Designer can create)
        # ... permission check
        return await self.repo.create(data, reporter_id)

    async def get(self, task_id: UUID, current_user_id: UUID) -> Task:
        task = await self.repo.get(task_id)
        if not task:
            raise NotFoundError("Task not found")
        # Permission check
        return task

    async def list(self, project_id: UUID, filters: TaskFilter, current_user_id: UUID) -> List[Task]:
        # Verify project access
        return await self.repo.list(project_id, filters)

    async def update(self, task_id: UUID, data: TaskUpdate, current_user_id: UUID) -> Task:
        task = await self.get(task_id, current_user_id)
        # Check permissions: assignee can update status, PM can update all
        # Check optimistic lock
        if data.version != task.version:
            raise ConflictError("Task has been modified by another user")
        return await self.repo.update(task, data)

    async def delete(self, task_id: UUID, current_user_id: UUID) -> None:
        task = await self.get(task_id, current_user_id)
        # Only PM/reporter can delete
        await self.repo.delete(task)

    async def get_blocked_tasks(self, task_id: UUID) -> List[UUID]:
        return await self.repo.get_blocked_tasks(task_id)

    async def check_cycle(self, task_id: UUID, depends_on_task_id: UUID) -> bool:
        """Return True if adding this dependency creates a cycle."""
        # DFS from depends_on_task_id to see if we reach task_id
        visited = set()
        stack = [depends_on_task_id]
        while stack:
            current = stack.pop()
            if current == task_id:
                return True
            if current in visited:
                continue
            visited.add(current)
            deps = await self.repo.get_direct_dependencies(current)
            stack.extend(deps)
        return False
```

### 5. API Router (`src/backend/api/tasks.py`)
```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from typing import List
from src.backend.api.dependencies import get_current_user, get_db
from src.backend.services.task_service import TaskService
from src.backend.schemas.task import (
    TaskCreate, TaskUpdate, TaskRead, TaskFilter, TaskDependencyCreate
)
from src.backend.schemas.user import UserRead

router = APIRouter(prefix="/api/projects/{project_id}/tasks", tags=["tasks"])

@router.post("", response_model=TaskRead, status_code=201)
async def create_task(
    project_id: UUID,
    data: TaskCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TaskService(db)
    task = await service.create(data, current_user.id, current_user.id)
    return task

@router.get("", response_model=List[TaskRead])
async def list_tasks(
    project_id: UUID,
    status: Optional[str] = None,
    assignee_id: Optional[UUID] = None,
    due_before: Optional[datetime] = None,
    due_after: Optional[datetime] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TaskService(db)
    filters = TaskFilter(status=status, assignee_id=assignee_id,
                        due_before=due_before, due_after=due_after, search=search)
    return await service.list(project_id, filters, current_user.id)

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    project_id: UUID,
    task_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TaskService(db)
    return await service.get(task_id, current_user.id)

@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    project_id: UUID,
    task_id: UUID,
    data: TaskUpdate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TaskService(db)
    return await service.update(task_id, data, current_user.id)

@router.delete("/{task_id}", status_code=204)
async def delete_task(
    project_id: UUID,
    task_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TaskService(db)
    await service.delete(task_id, current_user.id)

# Kanban endpoint
@router.get("/kanban", response_model=dict)
async def get_kanban_board(
    project_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TaskService(db)
    # Get all tasks, group by status
    filters = TaskFilter()
    tasks = await service.list(project_id, TaskFilter(), current_user.id)
    board = {"todo": [], "in_progress": [], "review": [], "done": []}
    for task in tasks:
        board[task.status].append(task)
    return board

# Reorder endpoint
@router.patch("/{task_id}/reorder", response_model=TaskRead)
async def reorder_task(
    project_id: UUID,
    task_id: UUID,
    data: TaskReorder,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Update status and/or position
    pass
```

---

## Acceptance Criteria (from contracts)
- [ ] `POST /api/projects/{project_id}/tasks` creates task with minimal fields
- [ ] `GET /api/tasks/{task_id}` returns task with relations
- [ ] `GET /api/projects/{project_id}/tasks` supports filters
- [ ] `PATCH /api/tasks/{task_id}` with optimistic lock (409 on conflict)
- [ ] `DELETE /api/tasks/{task_id}` removes task
- [ ] RBAC: PM/Designer create; Assignee update status; Viewer read-only
- [ ] Filters: status, assignee, due_before, due_after, search
- [ ] `GET /api/projects/{project_id}/tasks/kanban` returns grouped board

---

## Test Command
```bash
pytest .specify/specs/wave-4/contracts/test_wave4_contracts.py::TestTasksAPI -v
```