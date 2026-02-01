"""Task domain errors."""

from backend.src.domain.errors.base import DomainError


class TaskError(DomainError):
    """Base exception for task errors."""

    pass


class InvalidStatusTransitionError(TaskError):
    """Raised when task status transition is not allowed."""

    def __init__(self, current: str, target: str):
        super().__init__(
            f"Cannot transition from {current} to {target}",
            status=400,
        )


class TaskNotSelectableError(TaskError):
    """Raised when task cannot be selected (dependencies not met or no difficulty)."""

    def __init__(self, task_id: str, reason: str = "has unfinished dependencies"):
        super().__init__(
            f"Task {task_id} {reason}",
            status=400,
        )
