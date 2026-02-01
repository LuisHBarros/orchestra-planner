from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import ProjectInvite


class ProjectInviteRepository(Protocol):
    async def get(self, project_invite_id: UUID) -> Optional[ProjectInvite]: ...

    async def create(self, project_invite: ProjectInvite) -> ProjectInvite: ...

    async def update(self, project_invite: ProjectInvite) -> ProjectInvite: ...

    async def delete(self, project_invite_id: UUID) -> None: ...
