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
from backend.src.domain.errors.project import (
    ManagerRequiredError,
    ProjectAccessDeniedError,
    ProjectError,
    ProjectNotFoundError,
)
from backend.src.domain.errors.task import (
    InvalidStatusTransitionError,
    TaskError,
    TaskNotSelectableError,
)
from backend.src.domain.errors.workload import (
    WorkloadError,
    WorkloadExceededError,
)

__all__ = [
    "DomainError",
    "AuthError",
    "InvalidTokenError",
    "InvalidTokenPayloadError",
    "MagicLinkExpiredError",
    "UserNotFoundError",
    "TaskError",
    "InvalidStatusTransitionError",
    "TaskNotSelectableError",
    "WorkloadError",
    "WorkloadExceededError",
    "ProjectError",
    "ProjectNotFoundError",
    "ProjectAccessDeniedError",
    "ManagerRequiredError",
]
