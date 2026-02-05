"""SQLAlchemy model for Task entity."""

from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.domain.entities.task import Task, TaskStatus
from backend.src.infrastructure.db.base import Base


class TaskModel(Base):
    """Database model for tasks."""

    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    difficulty_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status", native_enum=False),
        default=TaskStatus.TODO,
        server_default=TaskStatus.TODO.value,
    )
    assignee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project_members.id"),
        nullable=True,
        index=True,
    )
    required_role_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("roles.id"),
        nullable=True,
        index=True,
    )
    progress_percent: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    expected_start_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expected_end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    actual_end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    @classmethod
    def from_entity(cls, task: Task) -> Self:
        """Create a TaskModel from a domain Task entity."""
        return cls(
            id=task.id,
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            difficulty_points=task.difficulty_points,
            status=task.status,
            assignee_id=task.assignee_id,
            required_role_id=task.required_role_id,
            progress_percent=task.progress_percent,
            expected_start_date=task.expected_start_date,
            expected_end_date=task.expected_end_date,
            actual_end_date=task.actual_end_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    def to_entity(self) -> Task:
        """Convert this TaskModel into a domain Task entity."""
        return Task(
            id=self.id,
            project_id=self.project_id,
            title=self.title,
            description=self.description or "",
            difficulty_points=self.difficulty_points,
            status=self.status,
            assignee_id=self.assignee_id,
            required_role_id=self.required_role_id,
            progress_percent=self.progress_percent,
            expected_start_date=self.expected_start_date,
            expected_end_date=self.expected_end_date,
            actual_end_date=self.actual_end_date,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
