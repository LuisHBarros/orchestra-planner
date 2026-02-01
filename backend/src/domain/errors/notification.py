"""Notification domain errors."""

from backend.src.domain.errors.base import DomainError


class NotificationError(DomainError):
    """Base exception for notification-related errors."""

    pass


class NotificationDeliveryError(NotificationError):
    """Raised when notification cannot be delivered."""

    def __init__(self, recipient: str, channel: str, detail: str):
        super().__init__(
            f"Failed to deliver {channel} notification to {recipient}: {detail}",
            status=502,
        )
        self.recipient = recipient
        self.channel = channel
        self.detail = detail


class EmailDeliveryError(NotificationError):
    """Raised when email notification fails (daily reports, alerts)."""

    def __init__(self, recipient: str, detail: str):
        super().__init__(
            f"Failed to send email to {recipient}: {detail}",
            status=502,
        )
        self.recipient = recipient
        self.detail = detail


class InvalidRecipientError(NotificationError):
    """Raised when recipient is invalid or unreachable."""

    def __init__(self, recipient: str):
        super().__init__(
            f"Invalid or unreachable recipient: {recipient}",
            status=400,
        )
        self.recipient = recipient


class NotificationTemplateError(NotificationError):
    """Raised when notification template cannot be rendered."""

    def __init__(self, template_name: str, detail: str):
        super().__init__(
            f"Failed to render template '{template_name}': {detail}",
            status=500,
        )
        self.template_name = template_name
        self.detail = detail
