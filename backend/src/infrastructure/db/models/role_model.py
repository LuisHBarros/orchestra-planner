"""SQLAlchemy model for Role entity."""

from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.domain.entities.role import Role
from backend.src.infrastructure.db.base import Base


class RoleModel(Base):
    """Database model for roles."""

    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_roles_project_id_name"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    @classmethod
    def from_entity(cls, role: Role) -> Self:
        """Create a RoleModel from a domain Role entity."""
        return cls(
            id=role.id,
            project_id=role.project_id,
            name=role.name,
            created_at=role.created_at,
        )

    def to_entity(self) -> Role:
        """Convert this RoleModel into a domain Role entity."""
        return Role(
            id=self.id,
            project_id=self.project_id,
            name=self.name,
            created_at=self.created_at,
        )
