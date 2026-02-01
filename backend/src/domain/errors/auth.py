"""Authentication domain errors."""

from backend.src.domain.errors.base import DomainError


class AuthError(DomainError):
    """Base exception for authentication errors."""

    pass


class UserNotFoundError(AuthError):
    """Raised when user does not exist."""

    def __init__(self, identifier: str):
        super().__init__(
            f"User not found: {identifier}",
            status=404,
        )


class UserAlreadyExistsError(AuthError):
    """Raised when user already exists."""

    def __init__(self, email: str):
        super().__init__(
            f"User already exists: {email}",
            status=409,
        )


class InvalidTokenError(AuthError):
    """Raised when magic link token is invalid."""

    def __init__(self):
        super().__init__(
            "Invalid or expired token",
            status=400,
        )


class InvalidTokenPayloadError(AuthError):
    """Raised when token payload is malformed or missing required fields."""

    def __init__(self):
        super().__init__(
            "Token payload is invalid or missing required fields",
            status=400,
        )


class MagicLinkExpiredError(AuthError):
    """Raised when magic link has expired (15 min)."""

    def __init__(self):
        super().__init__(
            "Magic link has expired",
            status=400,
        )
