"""SQLAlchemy model for Project entity."""

from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.domain.entities.project import Project
from backend.src.infrastructure.db.base import Base


class ProjectModel(Base):
    """Database model for projects."""

    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    manager_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    llm_provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    llm_api_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    @classmethod
    def from_entity(cls, project: Project) -> Self:
        """Create a ProjectModel from a domain Project entity."""
        return cls(
            id=project.id,
            manager_id=project.manager_id,
            name=project.name,
            description=project.description,
            llm_provider=project.llm_provider,
            llm_api_key_encrypted=project.llm_api_key_encrypted,
            expected_end_date=project.expected_end_date,
            created_at=project.created_at,
        )

    def to_entity(self) -> Project:
        """Convert this ProjectModel into a domain Project entity."""
        return Project(
            id=self.id,
            manager_id=self.manager_id,
            name=self.name,
            description=self.description or "",
            llm_provider=self.llm_provider,
            llm_api_key_encrypted=self.llm_api_key_encrypted,
            expected_end_date=self.expected_end_date,
            created_at=self.created_at,
        )
