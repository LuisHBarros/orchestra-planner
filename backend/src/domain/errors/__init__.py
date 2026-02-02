"""
Domain errors (business exceptions).

These exceptions represent violations of business rules and domain invariants.
They are part of the domain layer and should be raised by entities and use cases.
"""

from backend.src.domain.errors.auth import (
    AuthError,
    InvalidTokenError,
    InvalidTokenPayloadError,
    MagicLinkExpiredError,
    UserNotFoundError,
)
from backend.src.domain.errors.base import DomainError
from backend.src.domain.errors.invite import (
    InviteAlreadyAcceptedError,
    InviteError,
    InviteExpiredError,
    InviteNotFoundError,
    UserAlreadyMemberError,
)
from backend.src.domain.errors.llm import (
    LLMAPIKeyDecryptionError,
    LLMError,
    LLMInvalidResponseError,
    LLMNotConfiguredError,
    LLMProviderError,
    LLMRateLimitError,
)
from backend.src.domain.errors.notification import (
    EmailDeliveryError,
    InvalidRecipientError,
    NotificationDeliveryError,
    NotificationError,
    NotificationTemplateError,
)
from backend.src.domain.errors.project import (
    ManagerRequiredError,
    ProjectAccessDeniedError,
    ProjectError,
    ProjectNotFoundError,
)
from backend.src.domain.errors.task import (
    CircularDependencyError,
    InvalidStatusTransitionError,
    TaskError,
    TaskNotAssignedError,
    TaskNotFoundError,
    TaskNotOwnedError,
    TaskNotSelectableError,
)
from backend.src.domain.errors.workload import (
    WorkloadError,
    WorkloadExceededError,
)

__all__ = [
    # Base
    "DomainError",
    # Auth
    "AuthError",
    "InvalidTokenError",
    "InvalidTokenPayloadError",
    "MagicLinkExpiredError",
    "UserNotFoundError",
    # Task
    "TaskError",
    "TaskNotFoundError",
    "InvalidStatusTransitionError",
    "TaskNotSelectableError",
    "TaskNotAssignedError",
    "TaskNotOwnedError",
    "CircularDependencyError",
    # Workload
    "WorkloadError",
    "WorkloadExceededError",
    # Project
    "ProjectError",
    "ProjectNotFoundError",
    "ProjectAccessDeniedError",
    "ManagerRequiredError",
    # Invite
    "InviteError",
    "InviteNotFoundError",
    "InviteExpiredError",
    "InviteAlreadyAcceptedError",
    "UserAlreadyMemberError",
    # LLM
    "LLMError",
    "LLMNotConfiguredError",
    "LLMProviderError",
    "LLMRateLimitError",
    "LLMInvalidResponseError",
    "LLMAPIKeyDecryptionError",
    # Notification
    "NotificationError",
    "NotificationDeliveryError",
    "EmailDeliveryError",
    "InvalidRecipientError",
    "NotificationTemplateError",
]
