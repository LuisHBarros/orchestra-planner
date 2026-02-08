"""Service port interfaces."""

from backend.src.domain.ports.services.email_service import EmailMessage, EmailService
from backend.src.domain.ports.services.encryption_service import EncryptionService
from backend.src.domain.ports.services.llm_service import (
    DifficultyEstimation,
    LLMService,
    ProgressEstimation,
)
from backend.src.domain.ports.services.notification_service import (
    DailyReportData,
    NewTaskToastData,
    NotificationService,
    WorkloadAlertData,
)
from backend.src.domain.ports.services.token_service import TokenPair, TokenService
from backend.src.domain.ports.services.time_provider import TimeProvider

__all__ = [
    "EmailService",
    "EmailMessage",
    "EncryptionService",
    "TokenService",
    "TokenPair",
    "LLMService",
    "DifficultyEstimation",
    "ProgressEstimation",
    "NotificationService",
    "DailyReportData",
    "WorkloadAlertData",
    "NewTaskToastData",
    "TimeProvider",
]
