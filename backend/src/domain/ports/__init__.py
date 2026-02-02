"""
Domain ports (interfaces/protocols).

Ports define the contracts for external system interactions.
They are part of the domain because they represent the domain's
requirements from the outside world.
"""

from backend.src.domain.ports.repositories import (
    ProjectInviteRepository,
    ProjectMemberRepository,
    ProjectRepository,
    RoleRepository,
    TaskDependencyRepository,
    TaskLogRepository,
    TaskRepository,
    UserRepository,
)
from backend.src.domain.ports.services import (
    DailyReportData,
    DifficultyEstimation,
    EmailMessage,
    EmailService,
    EncryptionService,
    LLMService,
    NewTaskToastData,
    NotificationService,
    ProgressEstimation,
    TokenPair,
    TokenService,
    WorkloadAlertData,
)

__all__ = [
    # Repositories
    "ProjectInviteRepository",
    "ProjectMemberRepository",
    "ProjectRepository",
    "RoleRepository",
    "TaskDependencyRepository",
    "TaskLogRepository",
    "TaskRepository",
    "UserRepository",
    # Services
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
]
