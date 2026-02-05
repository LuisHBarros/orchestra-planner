"""SQLAlchemy model for ProjectInvite entity."""

from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.domain.entities.project_invite import InviteStatus, ProjectInvite
from backend.src.infrastructure.db.base import Base


class ProjectInviteModel(Base):
    """Database model for project invites."""

    __tablename__ = "project_invites"

    token: Mapped[str] = mapped_column(String(255), primary_key=True, unique=True)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id"),
        index=True,
    )
    role_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("roles.id"),
        index=True,
    )
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True,
    )
    status: Mapped[InviteStatus] = mapped_column(
        Enum(InviteStatus, name="invite_status", native_enum=False),
        default=InviteStatus.PENDING,
        server_default=InviteStatus.PENDING.value,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    @classmethod
    def from_entity(cls, invite: ProjectInvite) -> Self:
        """Create a ProjectInviteModel from a domain ProjectInvite entity."""
        return cls(
            token=invite.token,
            project_id=invite.project_id,
            role_id=invite.role_id,
            created_by=invite.created_by,
            status=invite.status,
            expires_at=invite.expires_at,
            created_at=invite.created_at,
        )

    def to_entity(self) -> ProjectInvite:
        """Convert this ProjectInviteModel into a domain ProjectInvite entity."""
        return ProjectInvite(
            token=self.token,
            project_id=self.project_id,
            role_id=self.role_id,
            created_by=self.created_by,
            status=self.status,
            expires_at=self.expires_at,
            created_at=self.created_at,
        )
