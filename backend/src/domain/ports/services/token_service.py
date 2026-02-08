from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol
from uuid import UUID


@dataclass
class TokenPair:
    """Value object representing access and refresh tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class TokenService(Protocol):
    """Port for token generation and verification operations."""

    async def generate_tokens(
        self, user_id: UUID, claims: Dict[str, Any] | None = None
    ) -> TokenPair: ...

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]: ...

    async def refresh_token(self, token: str) -> TokenPair | None: ...

    async def revoke_token(self, token: str) -> Optional[Dict[str, Any]]: ...
