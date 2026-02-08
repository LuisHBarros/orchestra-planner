"""SQLAlchemy model for Calendar entity."""

from __future__ import annotations

from datetime import date
from typing import Self
from uuid import UUID

from sqlalchemy import String
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.domain.entities.calendar import Calendar, ExclusionDate
from backend.src.infrastructure.db.base import Base


class CalendarModel(Base):
    """Database model for project calendars."""

    __tablename__ = "project_calendars"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        unique=True,
        index=True,
        nullable=False,
    )
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", server_default="UTC")
    exclusion_dates: Mapped[list[date]] = mapped_column(
        ARRAY(sa.Date), default=list, server_default="{}"
    )

    @classmethod
    def from_entity(cls, calendar: Calendar) -> Self:
        """Create a CalendarModel from a domain Calendar entity."""
        return cls(
            id=calendar.id,
            project_id=calendar.project_id,
            timezone=calendar.timezone,
            exclusion_dates=[d.day for d in calendar.exclusion_dates],
        )

    def to_entity(self) -> Calendar:
        """Convert this CalendarModel into a domain Calendar entity."""
        exclusions = frozenset(
            ExclusionDate(d) for d in (self.exclusion_dates or [])
        )
        return Calendar(
            id=self.id,
            project_id=self.project_id,
            timezone=self.timezone or "UTC",
            exclusion_dates=exclusions,
        )
