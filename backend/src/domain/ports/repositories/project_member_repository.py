from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import ProjectMember


class ProjectMemberRepository(Protocol):
    """Port for project member persistence operations."""

    async def find_by_id(self, project_member_id: UUID) -> Optional[ProjectMember]: ...

    async def find_by_project(self, project_id: UUID) -> list[ProjectMember]: ...

    async def list_by_project(
        self, project_id: UUID, *, limit: int, offset: int
    ) -> list[ProjectMember]: ...

    async def count_by_project(self, project_id: UUID) -> int: ...

    async def find_by_project_and_user(
        self, project_id: UUID, user_id: UUID
    ) -> Optional[ProjectMember]: ...

    async def save(self, project_member: ProjectMember) -> ProjectMember: ...

    async def delete(self, project_member_id: UUID) -> None: ...
