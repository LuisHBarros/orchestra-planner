from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import ProjectMember


class ProjectMemberRepository(Protocol):
    async def get(self, project_member_id: UUID) -> Optional[ProjectMember]: ...

    async def create(self, project_member: ProjectMember) -> ProjectMember: ...

    async def update(self, project_member: ProjectMember) -> ProjectMember: ...

    async def delete(self, project_member_id: UUID) -> None: ...
