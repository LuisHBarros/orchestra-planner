from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import TaskLog


class TaskLogRepository(Protocol):
    async def get(self, task_log_id: UUID) -> Optional[TaskLog]: ...

    async def create(self, task_log: TaskLog) -> TaskLog: ...

    async def update(self, task_log: TaskLog) -> TaskLog: ...

    async def delete(self, task_log_id: UUID) -> None: ...
