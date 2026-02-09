from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import ProjectInvite


class ProjectInviteRepository(Protocol):
    """Port for project invite persistence operations."""

    async def find_by_token(self, token: str) -> Optional[ProjectInvite]: ...

    async def find_by_project(self, project_id: UUID) -> list[ProjectInvite]: ...

    async def list_by_project(
        self, project_id: UUID, *, limit: int, offset: int
    ) -> list[ProjectInvite]: ...

    async def count_by_project(self, project_id: UUID) -> int: ...

    async def save(self, project_invite: ProjectInvite) -> ProjectInvite: ...

    async def delete(self, token: str) -> None: ...
