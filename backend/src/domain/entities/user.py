"""User entity definition."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
import hashlib
import secrets


# Magic link expiration time as per BR-AUTH-002
MAGIC_LINK_EXPIRATION_MINUTES = 15


@dataclass
class User:
    """
    Registered individual in the system.
    
    BR-AUTH-001: Users authenticate via Magic Link (email-based token).
    BR-AUTH-002: Magic Link is valid for one-time use and expires after 15 minutes.
    BR-AUTH-003: Email addresses are unique identifiers and case-insensitive.
    """
    email: str
    name: str
    id: UUID = field(default_factory=uuid4)
    magic_link_token_hash: str | None = field(default=None)
    token_expires_at: datetime | None = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate and normalize user attributes."""
        if not self.email or not self.email.strip():
            raise ValueError("Email cannot be empty")
        if not self.name or not self.name.strip():
            raise ValueError("Name cannot be empty")
        # BR-AUTH-003: Case-insensitive email
        self.email = self.email.strip().lower()
        self.name = self.name.strip()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def generate_magic_link_token(self) -> str:
        """
        Generate a new magic link token for authentication.
        
        Returns the raw token (to be sent to user).
        The hashed version is stored in magic_link_token_hash.
        """
        raw_token = secrets.token_urlsafe(32)
        self.magic_link_token_hash = self._hash_token(raw_token)
        self.token_expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=MAGIC_LINK_EXPIRATION_MINUTES
        )
        return raw_token

    def verify_magic_link_token(self, raw_token: str) -> bool:
        """
        Verify a magic link token.
        
        BR-AUTH-002: Token is valid for one-time use and expires after 15 minutes.
        """
        if not self.magic_link_token_hash or not self.token_expires_at:
            return False
        if datetime.now(timezone.utc) > self.token_expires_at:
            return False
        return self._hash_token(raw_token) == self.magic_link_token_hash

    def clear_magic_link_token(self) -> None:
        """Clear the magic link token after successful verification (one-time use)."""
        self.magic_link_token_hash = None
        self.token_expires_at = None

    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash a token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()
