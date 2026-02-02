from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import User


class UserRepository(Protocol):
    """Port for user persistence operations."""

    async def save(self, user: User) -> User: ...

    async def find_by_id(self, user_id: UUID) -> Optional[User]: ...

    async def find_by_email(self, email: str) -> Optional[User]: ...

    async def update(self, user: User) -> User: ...

    async def delete(self, user_id: UUID) -> None: ...
