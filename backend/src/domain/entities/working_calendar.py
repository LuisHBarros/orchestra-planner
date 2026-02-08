"""Working calendar value object for per-project scheduling rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from backend.src.domain.entities.calendar import Calendar

@dataclass(frozen=True)
class WorkingCalendar:
    """
    Per-project working calendar (BR-WDAY-001/002).

    Uses a default weekly schedule plus exclusion dates.
    """

    timezone: str = "UTC"
    working_weekdays: frozenset[int] = field(
        default_factory=lambda: frozenset({0, 1, 2, 3, 4})
    )
    exclusion_dates: frozenset[date] = field(default_factory=frozenset)

    def is_working_day(self, dt: datetime) -> bool:
        """Return True if the datetime falls on a working day."""
        local_date = self._local_date(dt)
        if local_date in self.exclusion_dates:
            return False
        return local_date.weekday() in self.working_weekdays

    def _local_date(self, dt: datetime) -> date:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        local_dt = dt.astimezone(ZoneInfo(self.timezone))
        return local_dt.date()

    @classmethod
    def default(cls) -> "WorkingCalendar":
        """Default calendar is Monday through Friday (BR-WDAY-003)."""
        return cls()

    @classmethod
    def from_calendar(cls, calendar: Calendar) -> "WorkingCalendar":
        """Create a WorkingCalendar from a Calendar entity."""
        return cls(
            timezone=calendar.timezone,
            exclusion_dates=frozenset(d.day for d in calendar.exclusion_dates),
        )
