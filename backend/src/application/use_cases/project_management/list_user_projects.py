from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import Project
from backend.src.domain.ports.unit_of_work import UnitOfWork


@dataclass
class ListUserProjectsInput:
    """Input for listing a user's projects."""

    user_id: UUID
    limit: int
    offset: int


@dataclass
class ListUserProjectsOutput:
    """Output containing paginated projects."""

    items: list[Project]
    total: int


class ListUserProjectsUseCase:
    """Use case for listing projects the user belongs to or manages."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, input: ListUserProjectsInput) -> ListUserProjectsOutput:
        async with self.uow:
            items = await self.uow.project_repository.list_by_user(
                input.user_id, limit=input.limit, offset=input.offset
            )
            total = await self.uow.project_repository.count_by_user(input.user_id)
        return ListUserProjectsOutput(items=items, total=total)
