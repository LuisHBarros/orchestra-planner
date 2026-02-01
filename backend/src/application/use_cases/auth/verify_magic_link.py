from uuid import UUID

from backend.src.domain.entities import User
from backend.src.domain.errors import (
    InvalidTokenError,
    InvalidTokenPayloadError,
    UserNotFoundError,
)
from backend.src.domain.ports import TokenService, UserRepository


class VerifyMagicLinkUseCase:
    """Use case for verifying a magic link token."""

    def __init__(
        self,
        token_service: TokenService,
        user_repository: UserRepository,
    ):
        self.token_service = token_service
        self.user_repository = user_repository

    async def execute(self, token: str) -> User:
        """
        Verifies a magic link token and returns the authenticated User.

        Raises:
            InvalidTokenError: If token is invalid or expired.
            InvalidTokenPayloadError: If token payload is malformed.
            UserNotFoundError: If user no longer exists.
        """
        payload = await self.token_service.verify_token(token)

        if payload is None:
            raise InvalidTokenError()

        raw_user_id = payload.get("user_id")
        if raw_user_id is None:
            raise InvalidTokenPayloadError()

        try:
            user_id = UUID(str(raw_user_id))
        except ValueError:
            raise InvalidTokenPayloadError()

        user = await self.user_repository.find_by_id(user_id)

        if user is None:
            raise UserNotFoundError(str(user_id))

        return user
