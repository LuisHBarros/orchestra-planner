"""Port for persistent storage of revoked JWT token IDs (jti)."""

from __future__ import annotations

from typing import Protocol


class RevokedTokenStore(Protocol):
    """Persistent revoked-token storage used by token services."""

    async def revoke(self, jti: str, ttl_seconds: int) -> None: ...

    async def is_revoked(self, jti: str) -> bool: ...
