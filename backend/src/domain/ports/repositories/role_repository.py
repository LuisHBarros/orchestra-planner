from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import role


class RoleRepository(Protocol):
    async def get(self, role_id: UUID) -> Optional[role.Role]: ...

    async def create(self, role: role.Role) -> role.Role: ...

    async def update(self, role: role.Role) -> role.Role: ...

    async def delete(self, role_id: UUID) -> None: ...
