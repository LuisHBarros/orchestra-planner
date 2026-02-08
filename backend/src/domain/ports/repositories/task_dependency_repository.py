from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import TaskDependency


class TaskDependencyRepository(Protocol):
    """Port for task dependency persistence operations."""

    async def save(self, task_dependency: TaskDependency) -> TaskDependency: ...

    async def find_by_id(self, dependency_id: UUID) -> Optional[TaskDependency]: ...

    async def find_by_project(self, project_id: UUID) -> list[TaskDependency]: ...

    async def find_by_tasks(
        self, blocking_task_id: UUID, blocked_task_id: UUID
    ) -> Optional[TaskDependency]: ...

    async def delete(self, dependency_id: UUID) -> None: ...

    async def delete_by_tasks(self, blocking_task_id: UUID, blocked_task_id: UUID) -> None: ...
