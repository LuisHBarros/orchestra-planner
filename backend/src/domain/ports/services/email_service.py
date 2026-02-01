from dataclasses import dataclass
from typing import List, Optional, Protocol


@dataclass
class EmailMessage:
    """Value object representing an email message."""

    recipients: List[str]
    subject: str
    body_text: str
    body_html: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None


class EmailService(Protocol):
    """Port for email sending operations."""

    async def send_email(self, message: EmailMessage) -> None: ...
