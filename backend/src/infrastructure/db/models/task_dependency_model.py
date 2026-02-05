"""SQLAlchemy model for TaskDependency entity."""

from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.domain.entities.task_dependency import TaskDependency
from backend.src.infrastructure.db.base import Base


class TaskDependencyModel(Base):
    """Database model for task dependencies."""

    __tablename__ = "task_dependencies"

    blocking_task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tasks.id"),
        primary_key=True,
    )
    blocked_task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tasks.id"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    @classmethod
    def from_entity(cls, dependency: TaskDependency) -> Self:
        """Create a TaskDependencyModel from a domain TaskDependency entity."""
        return cls(
            blocking_task_id=dependency.blocking_task_id,
            blocked_task_id=dependency.blocked_task_id,
            created_at=dependency.created_at,
        )

    def to_entity(self) -> TaskDependency:
        """Convert this TaskDependencyModel into a domain TaskDependency entity."""
        return TaskDependency(
            blocking_task_id=self.blocking_task_id,
            blocked_task_id=self.blocked_task_id,
            created_at=self.created_at,
        )
