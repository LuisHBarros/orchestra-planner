from typing import Protocol
from uuid import UUID

from backend.src.domain.entities import TaskLog


class TaskLogRepository(Protocol):
    """Port for task log persistence operations.

    BR-ASSIGN-005: All assignments and un-assignments are logged in history.
    BR-ABANDON-002: Reason for abandonment is recorded.
    """

    async def save(self, task_log: TaskLog) -> TaskLog: ...

    async def find_by_task(self, task_id: UUID) -> list[TaskLog]: ...

    async def find_by_author(self, author_id: UUID) -> list[TaskLog]: ...
