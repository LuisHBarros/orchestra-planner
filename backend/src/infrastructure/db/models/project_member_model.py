"""SQLAlchemy model for ProjectMember entity."""

from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.domain.entities.project_member import ProjectMember
from backend.src.domain.entities.seniority_level import SeniorityLevel
from backend.src.infrastructure.db.base import Base


class ProjectMemberModel(Base):
    """Database model for project members."""

    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "user_id",
            name="uq_project_members_project_id_user_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id"),
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True,
    )
    role_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("roles.id"),
        index=True,
    )
    seniority_level: Mapped[SeniorityLevel] = mapped_column(
        Enum(SeniorityLevel, name="seniority_level", native_enum=False)
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    @classmethod
    def from_entity(cls, member: ProjectMember) -> Self:
        """Create a ProjectMemberModel from a domain ProjectMember entity."""
        return cls(
            id=member.id,
            project_id=member.project_id,
            user_id=member.user_id,
            role_id=member.role_id,
            seniority_level=member.seniority_level,
            joined_at=member.joined_at,
        )

    def to_entity(self) -> ProjectMember:
        """Convert this ProjectMemberModel into a domain ProjectMember entity."""
        return ProjectMember(
            id=self.id,
            project_id=self.project_id,
            user_id=self.user_id,
            role_id=self.role_id,
            seniority_level=self.seniority_level,
            joined_at=self.joined_at,
        )
