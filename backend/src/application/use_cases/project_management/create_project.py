from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import Project
from backend.src.domain.errors import UserNotFoundError
from backend.src.domain.ports.repositories import ProjectRepository, UserRepository
from backend.src.domain.ports.unit_of_work import UnitOfWork


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
        uow: UnitOfWork | None = None,
        user_repository: UserRepository | None = None,
        project_repository: ProjectRepository | None = None,
    ):
        self.uow = uow
        self.user_repository = user_repository
        self.project_repository = project_repository

    async def execute(self, input: CreateProjectInput) -> Project:
        """
        Create a new project with the user as manager.

        BR-PROJ-001: The User who creates a Project is automatically assigned as the Manager.

        Raises:
            UserNotFoundError: If user doesn't exist.
        """
        if self.uow is not None:
            async with self.uow:
                user = await self.uow.user_repository.find_by_id(input.user_id)
                if not user:
                    raise UserNotFoundError(str(input.user_id))

                project = Project(
                    manager_id=user.id,
                    name=input.name,
                    description=input.description,
                )
                await self.uow.project_repository.save(project)
                await self.uow.commit()
            return project

        if self.user_repository is None or self.project_repository is None:
            raise RuntimeError("CreateProjectUseCase requires uow or repositories")

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
