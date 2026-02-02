from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import Role
from backend.src.domain.errors import ManagerRequiredError, ProjectNotFoundError
from backend.src.domain.ports.repositories import ProjectRepository, RoleRepository


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
        project_repository: ProjectRepository,
        role_repository: RoleRepository,
    ):
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
        project = await self.project_repository.find_by_id(input.project_id)
        if not project:
            raise ProjectNotFoundError(str(input.project_id))

        if not project.is_manager(input.requester_id):
            raise ManagerRequiredError("create role")

        role = Role(project_id=project.id, name=input.role_name)
        await self.role_repository.save(role)

        return role
