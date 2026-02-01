"""Project domain errors."""

from backend.src.domain.errors.base import DomainError


class ProjectError(DomainError):
    """Base exception for project errors."""

    pass


class ProjectNotFoundError(ProjectError):
    """Raised when project does not exist."""

    def __init__(self, project_id: str):
        super().__init__(
            f"Project not found: {project_id}",
            status=404,
        )


class ProjectAccessDeniedError(ProjectError):
    """Raised when user lacks permission to access project."""

    def __init__(self, user_id: str, project_id: str):
        super().__init__(
            f"User {user_id} does not have access to project {project_id}",
            status=403,
        )


class ManagerRequiredError(ProjectError):
    """Raised when operation requires manager role."""

    def __init__(self, operation: str):
        super().__init__(
            f"Manager role required for: {operation}",
            status=403,
        )


class ProjectAlreadyExistsError(ProjectError):
    """Raised when project already exists."""

    def __init__(self, project_id: str):
        super().__init__(
            f"Project already exists: {project_id}",
            status=409,
        )
