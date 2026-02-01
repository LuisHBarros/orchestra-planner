from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import task


class TaskRepository(Protocol):
    async def get(self, task_id: UUID) -> Optional[task.Task]: ...

    async def create(self, task: task.Task) -> task.Task: ...

    async def update(self, task: task.Task) -> task.Task: ...

    async def delete(self, task_id: UUID) -> None: ...
