from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import TaskDependency


class TaskDependencyRepository(Protocol):
    async def create(self, task_dependency: TaskDependency) -> TaskDependency: ...

    async def get(self, id: UUID) -> Optional[TaskDependency]: ...

    async def delete(self, id: UUID) -> None: ...
