from dataclasses import dataclass

from backend.src.domain.entities import User
from backend.src.domain.ports import EmailMessage, EmailService, UserRepository


@dataclass
class RequestMagicLinkInput:
    """Input for requesting a magic link."""

    email: str


class RequestMagicLinkUseCase:
    """Use case for requesting a magic link login."""

    def __init__(
        self,
        user_repository: UserRepository,
        email_service: EmailService,
    ):
        self.user_repository = user_repository
        self.email_service = email_service

    async def execute(self, input: RequestMagicLinkInput) -> None:
        """
        Request a magic link for the given email.

        Creates user if not exists, generates token, and sends email.
        Always returns success to prevent email enumeration (BR-AUTH-003).
        """
        email = input.email.strip().lower()

        user = await self.user_repository.find_by_email(email)
        if user is None:
            user = User(email=email, name="")

        token = user.generate_magic_link_token()

        await self.user_repository.save(user)

        message = EmailMessage(
            recipients=[email],
            subject="Your Magic Link Login",
            body_text=f"Click here to login: {token}",
            body_html=f"<p>Click <a href='?token={token}'>here</a> to login.</p>",
        )
        await self.email_service.send_email(message)
