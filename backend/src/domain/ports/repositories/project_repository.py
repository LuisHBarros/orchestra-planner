from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import Calendar, Project


class ProjectRepository(Protocol):
    """Port for project persistence operations."""

    async def find_by_id(self, project_id: UUID) -> Optional[Project]: ...

    async def find_by_id_with_calendar(
        self, project_id: UUID
    ) -> Optional[tuple[Project, Calendar | None]]: ...

    async def save(self, project: Project) -> Project: ...

    async def delete(self, project_id: UUID) -> None: ...
