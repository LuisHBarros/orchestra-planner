"""Redis-backed fixed-window rate limiter."""

from __future__ import annotations

from backend.src.domain.ports.services import RateLimitResult
from redis.asyncio import Redis


class RedisRateLimiter:
    """Rate limiter that uses Redis counters with TTL."""

    def __init__(self, redis: Redis, prefix: str = "ratelimit") -> None:
        self._redis = redis
        self._prefix = prefix

    def _key(self, key: str) -> str:
        return f"{self._prefix}:{key}"

    async def hit(self, key: str, limit: int, window_seconds: int) -> RateLimitResult:
        redis_key = self._key(key)
        current = await self._redis.incr(redis_key)
        if current == 1:
            await self._redis.expire(redis_key, window_seconds)

        ttl = await self._redis.ttl(redis_key)
        remaining = max(0, limit - current)
        if current > limit:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                retry_after_seconds=max(1, ttl) if ttl and ttl > 0 else window_seconds,
            )
        return RateLimitResult(allowed=True, remaining=remaining, retry_after_seconds=None)
