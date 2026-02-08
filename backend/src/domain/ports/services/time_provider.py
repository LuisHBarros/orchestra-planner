"""Port for time access to enable deterministic behavior."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class TimeProvider(Protocol):
    """Provides the current time."""

    def now(self) -> datetime:
        """Return the current time as timezone-aware datetime."""
        ...
