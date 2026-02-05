"""SQLAlchemy model for TaskLog entity."""

from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.domain.entities.task_log import TaskLog, TaskLogType
from backend.src.infrastructure.db.base import Base


class TaskLogModel(Base):
    """Database model for task logs."""

    __tablename__ = "task_logs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tasks.id"),
        index=True,
    )
    author_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project_members.id"),
        index=True,
    )
    log_type: Mapped[TaskLogType] = mapped_column(
        Enum(TaskLogType, name="task_log_type", native_enum=False)
    )
    content: Mapped[str] = mapped_column(Text, default="", server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    @classmethod
    def from_entity(cls, log: TaskLog) -> Self:
        """Create a TaskLogModel from a domain TaskLog entity."""
        return cls(
            id=log.id,
            task_id=log.task_id,
            author_id=log.author_id,
            log_type=log.log_type,
            content=log.content,
            created_at=log.created_at,
        )

    def to_entity(self) -> TaskLog:
        """Convert this TaskLogModel into a domain TaskLog entity."""
        return TaskLog(
            id=self.id,
            task_id=self.task_id,
            author_id=self.author_id,
            log_type=self.log_type,
            content=self.content or "",
            created_at=self.created_at,
        )
