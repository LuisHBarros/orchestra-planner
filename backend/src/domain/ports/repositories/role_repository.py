from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import Role


class RoleRepository(Protocol):
    """Port for role persistence operations."""

    async def find_by_id(self, role_id: UUID) -> Optional[Role]: ...

    async def save(self, role: Role) -> Role: ...

    async def delete(self, role_id: UUID) -> None: ...
