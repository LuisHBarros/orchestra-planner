from dataclasses import dataclass

from backend.src.domain.entities import User
from backend.src.domain.errors import InvalidTokenError, MagicLinkExpiredError
from backend.src.domain.ports import TokenPair, TokenService, UserRepository


@dataclass
class VerifyMagicLinkOutput:
    """Output for successful magic link verification."""

    user: User
    tokens: TokenPair


class VerifyMagicLinkUseCase:
    """Use case for verifying a magic link token."""

    def __init__(
        self,
        user_repository: UserRepository,
        token_service: TokenService,
    ):
        self.user_repository = user_repository
        self.token_service = token_service

    async def execute(self, token: str) -> VerifyMagicLinkOutput:
        """
        Verifies a magic link token and returns the authenticated User.

        Raises:
            InvalidTokenError: If token is invalid or expired.
            MagicLinkExpiredError: If token has expired.
        """
        if not token or not token.strip():
            raise InvalidTokenError()

        token_hash = User._hash_token(token)
        user = await self.user_repository.find_by_magic_link_token_hash(token_hash)
        if user is None:
            raise InvalidTokenError()

        if user.token_expires_at is None:
            raise InvalidTokenError()

        if not user.verify_magic_link_token(token):
            # Distinguish expired vs invalid
            if user.token_expires_at is not None:
                from backend.src.domain.time import utcnow

                if utcnow() > user.token_expires_at:
                    raise MagicLinkExpiredError()
            raise InvalidTokenError()

        user.clear_magic_link_token()
        await self.user_repository.save(user)
        tokens = await self.token_service.generate_tokens(user.id)
        return VerifyMagicLinkOutput(user=user, tokens=tokens)
