from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import Project
from backend.src.domain.errors import UserNotFoundError
from backend.src.domain.ports.repositories import ProjectRepository, UserRepository


@dataclass
class CreateProjectInput:
    """Input for creating a project."""

    user_id: UUID
    name: str
    description: str = ""


class CreateProjectUseCase:
    """Use case for creating a new project."""

    def __init__(
        self,
        user_repository: UserRepository,
        project_repository: ProjectRepository,
    ):
        self.user_repository = user_repository
        self.project_repository = project_repository

    async def execute(self, input: CreateProjectInput) -> Project:
        """
        Create a new project with the user as manager.

        BR-PROJ-001: The User who creates a Project is automatically assigned as the Manager.

        Raises:
            UserNotFoundError: If user doesn't exist.
        """
        user = await self.user_repository.find_by_id(input.user_id)
        if not user:
            raise UserNotFoundError(str(input.user_id))

        project = Project(
            manager_id=user.id,
            name=input.name,
            description=input.description,
        )
        await self.project_repository.save(project)

        return project
