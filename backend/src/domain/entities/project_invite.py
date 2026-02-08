"""ProjectInvite entity definition."""

import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID

from backend.src.domain.time import utcnow

# Default invite expiration time
INVITE_EXPIRATION_DAYS = 7


class InviteStatus(str, Enum):
    """Status of a project invitation (BR-INV-004)."""

    PENDING = "Pending"
    ACCEPTED = "Accepted"
    EXPIRED = "Expired"


@dataclass
class ProjectInvite:
    """
    An invitation to join a Project with a specific Role.

    BR-INV-001: Only Managers can generate invite links.
    BR-INV-002: An invite link is tied to a specific Project and a specific Role.
    BR-INV-003: Invite links are public tokens.
    BR-INV-004: An invite has three states: Pending, Accepted, Expired.
    BR-INV-005: A User cannot accept an invite if already a member.
    """

    project_id: UUID
    role_id: UUID
    created_by: UUID  # Manager ID
    token: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    status: InviteStatus = field(default=InviteStatus.PENDING)
    expires_at: datetime = field(
        default_factory=lambda: utcnow() + timedelta(days=INVITE_EXPIRATION_DAYS)
    )
    created_at: datetime = field(default_factory=utcnow)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProjectInvite):
            return NotImplemented
        return self.token == other.token

    def __hash__(self) -> int:
        return hash(self.token)

    @property
    def is_valid(self) -> bool:
        """Check if the invite is still valid (pending and not expired)."""
        if self.status != InviteStatus.PENDING:
            return False
        return utcnow() <= self.expires_at

    def accept(self) -> None:
        """
        Mark the invite as accepted.

        Raises:
            ValueError: If invite is not valid (already used or expired).
        """
        if not self.is_valid:
            if self.status == InviteStatus.ACCEPTED:
                raise ValueError("Invite has already been accepted")
            if self.status == InviteStatus.EXPIRED or utcnow() > self.expires_at:
                raise ValueError("Invite has expired")
            raise ValueError("Invite is not valid")
        self.status = InviteStatus.ACCEPTED

    def expire(self) -> None:
        """Mark the invite as expired."""
        if self.status == InviteStatus.PENDING:
            self.status = InviteStatus.EXPIRED

    def check_and_update_expiration(self) -> bool:
        """
        Check if invite should be expired based on time and update status.

        Returns True if status was changed to expired.
        """
        if self.status == InviteStatus.PENDING and utcnow() > self.expires_at:
            self.status = InviteStatus.EXPIRED
            return True
        return False
