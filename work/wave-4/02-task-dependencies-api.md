# Wave-4 Task 2: Task Dependencies API

**Skill:** `tdd`, `code-review`, `dag-validation`, `graph-algorithms`
**Estimated:** 45 min

---

## Goal
Implement DAG-based task dependencies with cycle detection and blocked status enforcement.

---

## Files to Create/Modify

### 1. Dependency Repository (`src/backend/db/repositories/task_dependency_repo.py`)
```python
from uuid import UUID
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.backend.models.task import TaskDependency, Task

class TaskDependencyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, task_id: UUID, depends_on_task_id: UUID) -> TaskDependency:
        dep = TaskDependency(task_id=task_id, depends_on_task_id=depends_on_task_id)
        self.session.add(dep)
        await self.session.flush()
        return dep

    async def remove(self, task_id: UUID, depends_on_task_id: UUID) -> bool:
        stmt = delete(TaskDependency).where(
            TaskDependency.task_id == task_id,
            TaskDependency.depends_on_task_id == depends_on_task_id
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_direct_dependencies(self, task_id: UUID) -> List[UUID]:
        stmt = select(TaskDependency.depends_on_task_id).where(TaskDependency.task_id == task_id)
        result = await self.session.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def get_dependents(self, task_id: UUID) -> List[UUID]:
        stmt = select(TaskDependency.task_id).where(TaskDependency.depends_on_task_id == task_id)
        result = await self.session.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def get_all_dependencies(self, task_id: UUID) -> List[UUID]:
        """Transitive closure: all tasks that task_id depends on (direct + indirect)."""
        stmt = """
        WITH RECURSIVE deps AS (
            SELECT depends_on_task_id FROM task_dependencies WHERE task_id = :tid
            UNION ALL
            SELECT td.depends_on_task_id
            FROM task_dependencies td
            JOIN deps d ON td.task_id = d.depends_on_task_id
        )
        SELECT depends_on_task_id FROM deps
        """
        result = await self.session.execute(text(stmt), {"task_id": task_id})
        return [row[0] for row in result.fetchall()]

    async def get_all_dependents(self, task_id: UUID) -> List[UUID]:
        """Transitive closure: all tasks that depend on task_id (direct + indirect)."""
        stmt = """
        WITH RECURSIVE deps AS (
            SELECT task_id FROM task_dependencies WHERE depends_on_task_id = :tid
            UNION ALL
            SELECT td.task_id
            FROM task_dependencies td
            JOIN deps d ON td.depends_on_task_id = d.task_id
        )
        SELECT task_id FROM deps
        """
        result = await self.session.execute(text(stmt), {"task_id": task_id})
        return [row[0] for row in result.fetchall()]

    async def has_path(self, from_task: UUID, to_task: UUID) -> bool:
        """Check if there's a path from from_task to to_task (cycle detection)."""
        visited = set()
        stack = [from_task]
        while stack:
            current = stack.pop()
            if current == to_task:
                return True
            if current in visited:
                continue
            visited.add(current)
            deps = await self.get_direct_dependencies(current)
            stack.extend(deps)
        return False
```

### 2. Dependency Service (`src/backend/services/task_dependency_service.py`)
```python
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.db.repositories.task_dependency_repo import TaskDependencyRepository
from src.backend.db.repositories.task_repo import TaskRepository
from src.backend.core.exceptions import ConflictError, NotFoundError

class TaskDependencyService:
    def __init__(self, session: AsyncSession):
        self.repo = TaskDependencyRepository(session)
        self.task_repo = TaskRepository(session)

    async def add_dependency(self, task_id: UUID, depends_on_task_id: UUID, current_user_id: UUID) -> TaskDependency:
        # Verify both tasks exist and user has access
        # ...
        # Cycle detection
        if await self.repo.has_path(depends_on_task_id, task_id):
            raise ConflictError("Adding this dependency would create a cycle")
        # Self-dependency check
        if task_id == depends_on_task_id:
            raise ConflictError("Task cannot depend on itself")
        return await self.repo.add(task_id, depends_on_task_id)

    async def remove_dependency(self, task_id: UUID, depends_on_task_id: UUID, current_user_id: UUID) -> bool:
        # Verify access
        return await self.repo.remove(task_id, depends_on_task_id)

    async def get_direct_dependencies(self, task_id: UUID) -> List[UUID]:
        return await self.repo.get_direct_dependencies(task_id)

    async def get_all_dependencies(self, task_id: UUID) -> List[UUID]:
        return await self.repo.get_all_dependencies(task_id)

    async def get_all_dependents(self, task_id: UUID) -> List[UUID]:
        return await self.repo.get_all_dependents(task_id)

    async def is_blocked(self, task_id: UUID) -> bool:
        """Check if task has any unfinished dependencies."""
        deps = await self.repo.get_direct_dependencies(task_id)
        if not deps:
            return False
        # Check if any dependency is not 'done'
        from src.backend.models.task import Task
        from src.backend.db.repositories.task_repo import TaskRepository
        task_repo = TaskRepository(self.session)
        for dep_id in deps:
            task = await task_repo.get(dep_id)
            if task and task.status != "done":
                return True
        return False

    async def get_blocked_tasks(self, task_id: UUID) -> List[UUID]:
        """Return all tasks that are blocked by task_id (transitive)."""
        return await self.repo.get_all_dependents(task_id)

    async def get_transitive_dependencies(self, task_id: UUID) -> List[UUID]:
        return await self.repo.get_all_dependencies(task_id)

    async def get_transitive_dependents(self, task_id: UUID) -> List[UUID]:
        return await self.repo.get_all_dependents(task_id)
```

### 3. API Router (`src/backend/api/task_dependencies.py`)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List
from src.backend.api.dependencies import get_current_user, get_db
from src.backend.services.task_dependency_service import TaskDependencyService
from src.backend.schemas.task_dependency import TaskDependencyCreate, TaskDependencyRead
from src.backend.schemas.user import UserRead

router = APIRouter(prefix="/api/tasks/{task_id}/dependencies", tags=["task-dependencies"])

@router.post("", response_model=TaskDependencyRead, status_code=201)
async def add_dependency(
    task_id: UUID,
    data: TaskDependencyCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TaskDependencyService(db)
    dep = await service.add_dependency(task_id, data.depends_on_task_id, current_user.id)
    # Fetch depends_on_task title for response
    return TaskDependencyRead(
        task_id=task_id,
        depends_on_task_id=data.depends_on_task_id,
        depends_on_task_title="",  # fetch if needed
        created_at=dep.created_at
    )

@router.delete("/{dep_id}", status_code=204)
async def remove_dependency(
    task_id: UUID,
    dep_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TaskDependencyService(db)
    # dep_id is the depends_on_task_id
    await service.remove_dependency(task_id, dep_id, current_user.id)

@router.get("", response_model=List[TaskDependencyRead])
async def list_dependencies(
    task_id: UUID,
    transitive: bool = False,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TaskDependencyService(db)
    if transitive:
        dep_ids = await service.get_all_dependencies(task_id)
    else:
        dep_ids = await service.get_direct_dependencies(task_id)
    # Fetch titles for each
    return [TaskDependencyRead(task_id=task_id, depends_on_task_id=d, depends_on_task_title="", created_at=None) for d in dep_ids]

@router.get("/blocked", response_model=bool)
async def check_blocked(
    task_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TaskDependencyService(db)
    return await service.is_blocked(task_id)

@router.get("/blocked-tasks", response_model=List[UUID])
async def get_blocked_tasks(
    task_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TaskDependencyService(db)
    return await service.get_blocked_tasks(task_id)
```

### 4. Schema (`src/backend/schemas/task_dependency.py`)
```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class TaskDependencyCreate(BaseModel):
    depends_on_task_id: UUID

class TaskDependencyRead(BaseModel):
    task_id: UUID
    depends_on_task_id: UUID
    depends_on_task_title: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
```

---

## Acceptance Criteria (from contracts)
- [ ] `POST /api/tasks/{task_id}/dependencies` adds dependency
- [ ] `DELETE /api/tasks/{task_id}/dependencies/{dep_id}` removes
- [ ] Cycle detection: `400` if cycle created
- [ ] Self-dependency rejected
- [ ] `GET /api/tasks/{task_id}/dependencies` lists direct deps
- [ ] `GET /api/tasks/{task_id}/dependencies?transitive=true` lists transitive
- [ ] Blocked status: task cannot move to `in_progress` if any dependency not `done`
- [ ] `GET /api/tasks/{task_id}/dependencies/blocked` returns boolean
- [ ] `GET /api/tasks/{task_id}/dependencies/blocked-tasks` lists all blocked tasks

---

## Test Command
```bash
pytest .specify/specs/wave-4/contracts/test_wave4_contracts.py::TestTaskDependencies -v
```