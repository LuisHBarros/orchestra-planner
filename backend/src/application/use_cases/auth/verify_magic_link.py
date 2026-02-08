from dataclasses import dataclass

from backend.src.domain.entities import User
from backend.src.domain.errors import InvalidTokenError, MagicLinkExpiredError
from backend.src.domain.ports import TokenPair, TokenService, UnitOfWork, UserRepository


@dataclass
class VerifyMagicLinkOutput:
    """Output for successful magic link verification."""

    user: User
    tokens: TokenPair


class VerifyMagicLinkUseCase:
    """Use case for verifying a magic link token."""

    def __init__(
        self,
        token_service: TokenService,
        uow: UnitOfWork | None = None,
        user_repository: UserRepository | None = None,
    ):
        self.uow = uow
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

        if self.uow is not None:
            async with self.uow:
                token_hash = User._hash_token(token)
                user = await self.uow.user_repository.find_by_magic_link_token_hash(
                    token_hash
                )
                if user is None:
                    raise InvalidTokenError()

                if user.token_expires_at is None:
                    raise InvalidTokenError()

                if not user.verify_magic_link_token(token):
                    if user.token_expires_at is not None:
                        from backend.src.domain.time import utcnow

                        if utcnow() > user.token_expires_at:
                            raise MagicLinkExpiredError()
                    raise InvalidTokenError()

                user.clear_magic_link_token()
                await self.uow.user_repository.save(user)
                await self.uow.commit()
        else:
            if self.user_repository is None:
                raise RuntimeError(
                    "VerifyMagicLinkUseCase requires uow or user_repository"
                )
            token_hash = User._hash_token(token)
            user = await self.user_repository.find_by_magic_link_token_hash(token_hash)
            if user is None:
                raise InvalidTokenError()
            if user.token_expires_at is None:
                raise InvalidTokenError()
            if not user.verify_magic_link_token(token):
                if user.token_expires_at is not None:
                    from backend.src.domain.time import utcnow

                    if utcnow() > user.token_expires_at:
                        raise MagicLinkExpiredError()
                raise InvalidTokenError()
            user.clear_magic_link_token()
            await self.user_repository.save(user)

        tokens = await self.token_service.generate_tokens(user.id)
        return VerifyMagicLinkOutput(user=user, tokens=tokens)
