from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import Project


class ProjectRepository(Protocol):
    """Port for project persistence operations."""

    async def find_by_id(self, project_id: UUID) -> Optional[Project]: ...

    async def list_by_user(
        self, user_id: UUID, *, limit: int, offset: int
    ) -> list[Project]: ...

    async def count_by_user(self, user_id: UUID) -> int: ...

    async def save(self, project: Project) -> Project: ...

    async def delete(self, project_id: UUID) -> None: ...
