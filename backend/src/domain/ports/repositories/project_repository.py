from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import Project


class ProjectRepository(Protocol):
    async def find_by_id(self, project_id: UUID) -> Optional[Project]: ...

    async def create(self, project: Project) -> Project: ...

    async def update(self, project: Project) -> Project: ...

    async def delete(self, project_id: UUID) -> None: ...
