from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import Project
from backend.src.domain.errors import ProjectAccessDeniedError, ProjectNotFoundError
from backend.src.domain.ports import ProjectMemberRepository, ProjectRepository
from backend.src.domain.ports.unit_of_work import UnitOfWork


@dataclass
class GetProjectDetailsInput:
    """Input for getting project details."""

    project_id: UUID
    requester_id: UUID  # The user requesting access


@dataclass
class GetProjectDetailsOutput:
    """Output containing project details."""

    project: Project
    is_manager: bool


class GetProjectDetailsUseCase:
    """Use case for retrieving project details."""

    def __init__(
        self,
        uow: UnitOfWork | None = None,
        project_repository: ProjectRepository | None = None,
        project_member_repository: ProjectMemberRepository | None = None,
    ):
        self.uow = uow
        self.project_repository = project_repository
        self.project_member_repository = project_member_repository

    async def execute(self, input: GetProjectDetailsInput) -> GetProjectDetailsOutput:
        """
        Get project details for an authorized member.

        BR-PROJ-002: Only project members can view project details.

        Raises:
            ProjectNotFoundError: If project doesn't exist.
            ProjectAccessDeniedError: If requester is not a project member.
        """
        if self.uow is not None:
            async with self.uow:
                project = await self.uow.project_repository.find_by_id(input.project_id)
                if project is None:
                    raise ProjectNotFoundError(str(input.project_id))

                member = await self.uow.project_member_repository.find_by_project_and_user(
                    input.project_id, input.requester_id
                )
                if member is None and not project.is_manager(input.requester_id):
                    raise ProjectAccessDeniedError(
                        str(input.requester_id), str(input.project_id)
                    )
            return GetProjectDetailsOutput(
                project=project,
                is_manager=project.is_manager(input.requester_id),
            )

        if self.project_repository is None or self.project_member_repository is None:
            raise RuntimeError("GetProjectDetailsUseCase requires uow or repositories")
        project = await self.project_repository.find_by_id(input.project_id)
        if project is None:
            raise ProjectNotFoundError(str(input.project_id))
        member = await self.project_member_repository.find_by_project_and_user(
            input.project_id, input.requester_id
        )
        if member is None and not project.is_manager(input.requester_id):
            raise ProjectAccessDeniedError(str(input.requester_id), str(input.project_id))

        return GetProjectDetailsOutput(
            project=project,
            is_manager=project.is_manager(input.requester_id),
        )
