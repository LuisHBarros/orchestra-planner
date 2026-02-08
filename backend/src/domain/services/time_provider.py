"""Time provider implementations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from backend.src.domain.ports.services.time_provider import TimeProvider


@dataclass(frozen=True)
class SystemTimeProvider(TimeProvider):
    """Default provider using system UTC time."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


@dataclass(frozen=True)
class FixedTimeProvider(TimeProvider):
    """Fixed time provider for deterministic tests."""

    fixed_time: datetime

    def now(self) -> datetime:
        return self.fixed_time
