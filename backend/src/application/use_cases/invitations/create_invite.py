"""Create invite use case."""

from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import ProjectInvite
from backend.src.domain.errors import ManagerRequiredError, ProjectNotFoundError
from backend.src.domain.ports.repositories import (
    ProjectInviteRepository,
    ProjectRepository,
    RoleRepository,
)


@dataclass
class CreateInviteInput:
    """Input for creating a project invitation."""

    project_id: UUID
    role_id: UUID
    requester_id: UUID


@dataclass
class CreateInviteOutput:
    """Output containing the created invitation."""

    invite: ProjectInvite
    invite_url: str


class CreateInviteUseCase:
    """Use case for creating a project invitation."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        role_repository: RoleRepository,
        project_invite_repository: ProjectInviteRepository,
        base_url: str = "http://localhost:8000",
    ):
        self.project_repository = project_repository
        self.role_repository = role_repository
        self.project_invite_repository = project_invite_repository
        self.base_url = base_url

    async def execute(self, input: CreateInviteInput) -> CreateInviteOutput:
        """
        Create an invitation link for a project.

        BR-INV-001: Only Managers can generate invite links.
        BR-INV-002: An invite link is tied to a specific Project and a specific Role.
        BR-INV-003: Invite links are public tokens.

        Raises:
            ProjectNotFoundError: If project doesn't exist.
            ManagerRequiredError: If requester is not the project manager.
        """
        project = await self.project_repository.find_by_id(input.project_id)
        if project is None:
            raise ProjectNotFoundError(str(input.project_id))

        if not project.is_manager(input.requester_id):
            raise ManagerRequiredError("create invitation")

        # Verify the role exists (optional validation)
        role = await self.role_repository.find_by_id(input.role_id)
        if role is None or role.project_id != input.project_id:
            raise ValueError(f"Role {input.role_id} not found in project")

        invite = ProjectInvite(
            project_id=input.project_id,
            role_id=input.role_id,
            created_by=input.requester_id,
        )

        await self.project_invite_repository.save(invite)

        invite_url = f"{self.base_url}/invites/{invite.token}"

        return CreateInviteOutput(invite=invite, invite_url=invite_url)
