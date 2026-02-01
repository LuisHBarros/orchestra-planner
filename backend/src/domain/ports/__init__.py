"""
Domain ports (interfaces/protocols).

Ports define the contracts for external system interactions.
They are part of the domain because they represent the domain's
requirements from the outside world.
"""

from backend.src.domain.ports.repositories.user_repository import UserRepository
from backend.src.domain.ports.services.email_service import EmailMessage, EmailService
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

__all__ = [
    # Repositories
    "UserRepository",
    # Services
    "EmailService",
    "EmailMessage",
    "TokenService",
    "TokenPair",
    "LLMService",
    "DifficultyEstimation",
    "ProgressEstimation",
    "NotificationService",
    "DailyReportData",
    "WorkloadAlertData",
    "NewTaskToastData",
]
