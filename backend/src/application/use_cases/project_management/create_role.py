from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import Role
from backend.src.domain.errors import ManagerRequiredError, ProjectNotFoundError
from backend.src.domain.ports.repositories import ProjectRepository, RoleRepository
from backend.src.domain.ports.unit_of_work import UnitOfWork


@dataclass
class CreateRoleInput:
    """Input for creating a role."""

    project_id: UUID
    requester_id: UUID
    role_name: str


class CreateRoleUseCase:
    """Use case for creating a new role in a project."""

    def __init__(
        self,
        uow: UnitOfWork | None = None,
        project_repository: ProjectRepository | None = None,
        role_repository: RoleRepository | None = None,
    ):
        self.uow = uow
        self.project_repository = project_repository
        self.role_repository = role_repository

    async def execute(self, input: CreateRoleInput) -> Role:
        """
        Create a new role in a project.

        BR-PROJ-004: Only the Manager can edit Project settings.

        Raises:
            ProjectNotFoundError: If project doesn't exist.
            ManagerRequiredError: If requester is not the project manager.
        """
        if self.uow is not None:
            async with self.uow:
                project = await self.uow.project_repository.find_by_id(input.project_id)
                if not project:
                    raise ProjectNotFoundError(str(input.project_id))

                if not project.is_manager(input.requester_id):
                    raise ManagerRequiredError("create role")

                role = Role(project_id=project.id, name=input.role_name)
                await self.uow.role_repository.save(role)
                await self.uow.commit()
            return role

        if self.project_repository is None or self.role_repository is None:
            raise RuntimeError("CreateRoleUseCase requires uow or repositories")
        project = await self.project_repository.find_by_id(input.project_id)
        if not project:
            raise ProjectNotFoundError(str(input.project_id))
        if not project.is_manager(input.requester_id):
            raise ManagerRequiredError("create role")
        role = Role(project_id=project.id, name=input.role_name)
        await self.role_repository.save(role)

        return role
