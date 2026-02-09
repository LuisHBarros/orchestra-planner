from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.errors import ProjectAccessDeniedError, ProjectNotFoundError
from backend.src.domain.ports.unit_of_work import UnitOfWork


@dataclass
class ListProjectMembersInput:
    """Input for listing project members."""

    project_id: UUID
    requester_id: UUID
    limit: int
    offset: int


@dataclass
class EnrichedMember:
    """A project member enriched with user and role info."""

    id: UUID
    project_id: UUID
    user_id: UUID
    role_id: UUID
    seniority_level: str
    joined_at: str
    user_name: str
    user_email: str
    role_name: str


@dataclass
class ListProjectMembersOutput:
    """Output containing paginated enriched members."""

    items: list[EnrichedMember]
    total: int


class ListProjectMembersUseCase:
    """Use case for listing project members with enriched user/role info."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, input: ListProjectMembersInput) -> ListProjectMembersOutput:
        async with self.uow:
            project = await self.uow.project_repository.find_by_id(input.project_id)
            if project is None:
                raise ProjectNotFoundError(str(input.project_id))

            # Auth check: requester must be manager or member
            if not project.is_manager(input.requester_id):
                member = await self.uow.project_member_repository.find_by_project_and_user(
                    input.project_id, input.requester_id
                )
                if member is None:
                    raise ProjectAccessDeniedError(
                        str(input.requester_id), str(input.project_id)
                    )

            members = await self.uow.project_member_repository.list_by_project(
                input.project_id, limit=input.limit, offset=input.offset
            )
            total = await self.uow.project_member_repository.count_by_project(
                input.project_id
            )

            # Batch-load users and roles for enrichment
            user_ids = {m.user_id for m in members}
            role_ids = {m.role_id for m in members}

            users = {}
            for uid in user_ids:
                user = await self.uow.user_repository.find_by_id(uid)
                if user:
                    users[uid] = user

            roles = {}
            for rid in role_ids:
                role = await self.uow.role_repository.find_by_id(rid)
                if role:
                    roles[rid] = role

        enriched = []
        for m in members:
            user = users.get(m.user_id)
            role = roles.get(m.role_id)
            enriched.append(
                EnrichedMember(
                    id=m.id,
                    project_id=m.project_id,
                    user_id=m.user_id,
                    role_id=m.role_id,
                    seniority_level=m.seniority_level.value,
                    joined_at=m.joined_at.isoformat(),
                    user_name=user.name if user else "Unknown",
                    user_email=user.email if user else "",
                    role_name=role.name if role else "Unknown",
                )
            )

        return ListProjectMembersOutput(items=enriched, total=total)
