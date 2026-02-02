"""Invitation domain errors."""

from backend.src.domain.errors.base import DomainError


class InviteError(DomainError):
    """Base exception for invitation errors."""

    pass


class InviteNotFoundError(InviteError):
    """Raised when invite does not exist."""

    def __init__(self, token: str):
        super().__init__(
            f"Invite not found: {token}",
            status=404,
        )


class InviteExpiredError(InviteError):
    """Raised when invite has expired."""

    def __init__(self, token: str):
        super().__init__(
            f"Invite has expired: {token}",
            status=400,
        )


class InviteAlreadyAcceptedError(InviteError):
    """Raised when invite has already been accepted."""

    def __init__(self, token: str):
        super().__init__(
            f"Invite has already been accepted: {token}",
            status=400,
        )


class UserAlreadyMemberError(InviteError):
    """Raised when user is already a member of the project."""

    def __init__(self, user_id: str, project_id: str):
        super().__init__(
            f"User {user_id} is already a member of project {project_id}",
            status=409,
        )
