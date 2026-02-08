"""SMTP email service implementation."""

from __future__ import annotations

from backend.src.config.settings import AppSettings
from backend.src.domain.ports.services import EmailMessage


class SMTPEmailService:
    """Sends emails using SMTP."""

    def __init__(self, settings: AppSettings) -> None:
        required = {
            "SMTP_HOST": settings.smtp_host,
            "SMTP_USER": settings.smtp_user,
            "SMTP_PASSWORD": settings.smtp_password,
            "SMTP_FROM_EMAIL": settings.smtp_from_email,
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise RuntimeError(
                "Missing SMTP settings when EMAIL_PROVIDER != mock: "
                + ", ".join(missing)
            )

        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._username = settings.smtp_user
        self._password = settings.smtp_password
        self._from_email = settings.smtp_from_email
        self._use_tls = settings.smtp_use_tls

    async def send_email(self, message: EmailMessage) -> None:
        from email.message import EmailMessage as MIMEEmailMessage

        import aiosmtplib

        mime = MIMEEmailMessage()
        mime["From"] = self._from_email
        mime["To"] = ", ".join(message.recipients)
        mime["Subject"] = message.subject

        if message.cc:
            mime["Cc"] = ", ".join(message.cc)

        if message.body_html:
            mime.set_content(message.body_text)
            mime.add_alternative(message.body_html, subtype="html")
        else:
            mime.set_content(message.body_text)

        recipients = list(message.recipients)
        if message.cc:
            recipients.extend(message.cc)
        if message.bcc:
            recipients.extend(message.bcc)

        await aiosmtplib.send(
            mime,
            hostname=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            use_tls=self._use_tls,
            recipients=recipients,
        )
