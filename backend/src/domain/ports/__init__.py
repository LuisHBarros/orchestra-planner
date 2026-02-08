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
    RateLimitResult,
    RateLimiter,
    RevokedTokenStore,
    TokenPair,
    TokenService,
    WorkloadAlertData,
)
from backend.src.domain.ports.unit_of_work import UnitOfWork

__all__ = [
    # Unit of Work
    "UnitOfWork",
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
    "RevokedTokenStore",
    "RateLimiter",
    "RateLimitResult",
    "LLMService",
    "DifficultyEstimation",
    "ProgressEstimation",
    "NotificationService",
    "DailyReportData",
    "WorkloadAlertData",
    "NewTaskToastData",
]
