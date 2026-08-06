from uuid import UUID

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.task_dependency import TaskDependency


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

    async def get_direct_dependencies(self, task_id: UUID) -> list[UUID]:
        stmt = select(TaskDependency.depends_on_task_id).where(TaskDependency.task_id == task_id)
        result = await self.session.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def get_dependents(self, task_id: UUID) -> list[UUID]:
        stmt = select(TaskDependency.task_id).where(TaskDependency.depends_on_task_id == task_id)
        result = await self.session.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def get_all_dependencies(self, task_id: UUID) -> list[UUID]:
        """Transitive closure: all tasks that task_id depends on (direct + indirect)."""
        stmt = text("""
        WITH RECURSIVE deps AS (
            SELECT depends_on_task_id FROM task_dependencies WHERE task_id = :tid
            UNION ALL
            SELECT td.depends_on_task_id
            FROM task_dependencies td
            JOIN deps d ON td.task_id = d.depends_on_task_id
        )
        SELECT depends_on_task_id FROM deps
        """)
        result = await self.session.execute(stmt, {"tid": task_id})
        return [row[0] for row in result.fetchall()]

    async def get_all_dependents(self, task_id: UUID) -> list[UUID]:
        """Transitive closure: all tasks that depend on task_id (direct + indirect)."""
        stmt = text("""
        WITH RECURSIVE deps AS (
            SELECT task_id FROM task_dependencies WHERE depends_on_task_id = :tid
            UNION ALL
            SELECT td.task_id
            FROM task_dependencies td
            JOIN deps d ON td.depends_on_task_id = d.task_id
        )
        SELECT task_id FROM deps
        """)
        result = await self.session.execute(stmt, {"tid": task_id})
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
