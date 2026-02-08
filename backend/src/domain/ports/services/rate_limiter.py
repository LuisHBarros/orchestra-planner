"""Port for request rate limiting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RateLimitResult:
    """Result of a rate-limit check."""

    allowed: bool
    remaining: int
    retry_after_seconds: int | None = None


class RateLimiter(Protocol):
    """Leaky/bucket-like limiter abstraction."""

    async def hit(self, key: str, limit: int, window_seconds: int) -> RateLimitResult: ...
