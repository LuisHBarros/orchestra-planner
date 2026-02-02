"""Task domain errors."""

from backend.src.domain.errors.base import DomainError


class TaskError(DomainError):
    """Base exception for task errors."""

    pass


class TaskNotFoundError(TaskError):
    """Raised when task does not exist."""

    def __init__(self, task_id: str):
        super().__init__(
            f"Task not found: {task_id}",
            status=404,
        )


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


class TaskNotAssignedError(TaskError):
    """Raised when task is not assigned to any user."""

    def __init__(self, task_id: str):
        super().__init__(
            f"Task {task_id} is not assigned to anyone",
            status=400,
        )


class TaskNotOwnedError(TaskError):
    """Raised when user tries to modify a task they don't own."""

    def __init__(self, task_id: str, user_id: str):
        super().__init__(
            f"User {user_id} does not own task {task_id}",
            status=403,
        )


class CircularDependencyError(TaskError):
    """Raised when adding a dependency would create a circular reference."""

    def __init__(self, blocking_task_id: str, blocked_task_id: str):
        super().__init__(
            f"Adding dependency from {blocking_task_id} to {blocked_task_id} would create a cycle",
            status=400,
        )
