"""SQLAlchemy model for User entity."""

from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.domain.entities.user import User
from backend.src.infrastructure.db.base import Base


class UserModel(Base):
    """Database model for users."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    magic_link_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    @classmethod
    def from_entity(cls, user: User) -> Self:
        """Create a UserModel from a domain User entity."""
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            magic_link_token_hash=user.magic_link_token_hash,
            token_expires_at=user.token_expires_at,
            created_at=user.created_at,
        )

    def to_entity(self) -> User:
        """Convert this UserModel into a domain User entity."""
        return User(
            id=self.id,
            email=self.email,
            name=self.name,
            magic_link_token_hash=self.magic_link_token_hash,
            token_expires_at=self.token_expires_at,
            created_at=self.created_at,
        )
