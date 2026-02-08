from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import Project


class ProjectRepository(Protocol):
    """Port for project persistence operations."""

    async def find_by_id(self, project_id: UUID) -> Optional[Project]: ...

    async def save(self, project: Project) -> Project: ...

    async def delete(self, project_id: UUID) -> None: ...
