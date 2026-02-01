"""Workload domain errors."""

from backend.src.domain.errors.base import DomainError


class WorkloadError(DomainError):
    """Base exception for workload errors."""

    pass


class WorkloadExceededError(WorkloadError):
    """Raised when user cannot take more tasks (workload > 1.5)."""

    def __init__(self, current_ratio: float):
        super().__init__(
            f"Workload limit exceeded: {current_ratio:.2f} > 1.5",
            status=400,
        )
