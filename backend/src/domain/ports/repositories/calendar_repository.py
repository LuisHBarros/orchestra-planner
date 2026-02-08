from typing import Optional, Protocol
from uuid import UUID

from backend.src.domain.entities import Calendar


class CalendarRepository(Protocol):
    """Port for calendar persistence operations."""

    async def get_by_project_id(self, project_id: UUID) -> Optional[Calendar]: ...

    async def save(self, calendar: Calendar) -> Calendar: ...
