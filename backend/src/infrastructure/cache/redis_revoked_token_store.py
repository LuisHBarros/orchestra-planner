"""Redis-backed revoked-token store."""

from __future__ import annotations

from redis.asyncio import Redis


class RedisRevokedTokenStore:
    """Store revoked JWT ids in Redis with TTL."""

    def __init__(self, redis: Redis, prefix: str = "auth:revoked_jti") -> None:
        self._redis = redis
        self._prefix = prefix

    def _key(self, jti: str) -> str:
        return f"{self._prefix}:{jti}"

    async def revoke(self, jti: str, ttl_seconds: int) -> None:
        await self._redis.set(self._key(jti), "1", ex=max(1, ttl_seconds))

    async def is_revoked(self, jti: str) -> bool:
        value = await self._redis.get(self._key(jti))
        return value is not None
