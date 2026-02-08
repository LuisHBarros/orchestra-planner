"""Calendar entity for project-specific exclusions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ExclusionDate:
    """Value object representing a non-working date."""

    day: date


@dataclass
class Calendar:
    """Project calendar holding exclusion dates (BR-WDAY-002)."""

    project_id: UUID
    id: UUID = field(default_factory=uuid4)
    timezone: str = "UTC"
    exclusion_dates: frozenset[ExclusionDate] = field(default_factory=frozenset)

    def add_exclusion(self, exclusion_date: date) -> None:
        """Add an exclusion date to the calendar."""
        self.exclusion_dates = frozenset(
            {*(self.exclusion_dates), ExclusionDate(exclusion_date)}
        )

    def remove_exclusion(self, exclusion_date: date) -> None:
        """Remove an exclusion date from the calendar."""
        target = ExclusionDate(exclusion_date)
        if target in self.exclusion_dates:
            self.exclusion_dates = frozenset(
                d for d in self.exclusion_dates if d != target
            )
