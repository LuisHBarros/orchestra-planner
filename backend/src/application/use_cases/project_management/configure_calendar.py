"""Configure project calendar use case."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from backend.src.application.use_cases.project_management.recalculate_project_schedule import (
    RecalculateProjectScheduleInput,
    RecalculateProjectScheduleUseCase,
)
from backend.src.domain.entities import Calendar, ExclusionDate
from backend.src.domain.errors import ManagerRequiredError, ProjectNotFoundError
from backend.src.domain.ports.repositories import CalendarRepository, ProjectRepository
from backend.src.domain.ports.unit_of_work import UnitOfWork


@dataclass
class ConfigureCalendarInput:
    """Input for configuring a project calendar."""

    project_id: UUID
    requester_id: UUID
    timezone: str = "UTC"
    exclusion_dates: list[date] | None = None


class ConfigureCalendarUseCase:
    """Use case for updating project working calendar."""

    def __init__(
        self,
        recalculate_schedule_use_case: RecalculateProjectScheduleUseCase,
        uow: UnitOfWork | None = None,
        project_repository: ProjectRepository | None = None,
        calendar_repository: CalendarRepository | None = None,
    ) -> None:
        self.uow = uow
        self.project_repository = project_repository
        self.calendar_repository = calendar_repository
        self.recalculate_schedule_use_case = recalculate_schedule_use_case

    async def execute(self, input: ConfigureCalendarInput) -> Calendar:
        if self.uow is not None:
            async with self.uow:
                project = await self.uow.project_repository.find_by_id(input.project_id)
                if project is None:
                    raise ProjectNotFoundError(str(input.project_id))

                if not project.is_manager(input.requester_id):
                    raise ManagerRequiredError("configure calendar")

                calendar = await self.uow.calendar_repository.get_by_project_id(
                    input.project_id
                )
                if calendar is None:
                    calendar = Calendar(project_id=input.project_id)

                calendar.timezone = input.timezone
                dates = input.exclusion_dates or []
                calendar.exclusion_dates = frozenset(ExclusionDate(day=d) for d in dates)
                saved = await self.uow.calendar_repository.save(calendar)
                await self.uow.commit()
            await self.recalculate_schedule_use_case.execute(
                RecalculateProjectScheduleInput(project_id=input.project_id)
            )
            return saved

        if self.project_repository is None or self.calendar_repository is None:
            raise RuntimeError("ConfigureCalendarUseCase requires uow or repositories")
        project = await self.project_repository.find_by_id(input.project_id)
        if project is None:
            raise ProjectNotFoundError(str(input.project_id))
        if not project.is_manager(input.requester_id):
            raise ManagerRequiredError("configure calendar")
        calendar = await self.calendar_repository.get_by_project_id(input.project_id)
        if calendar is None:
            calendar = Calendar(project_id=input.project_id)
        calendar.timezone = input.timezone
        dates = input.exclusion_dates or []
        calendar.exclusion_dates = frozenset(ExclusionDate(day=d) for d in dates)
        saved = await self.calendar_repository.save(calendar)
        await self.recalculate_schedule_use_case.execute(
            RecalculateProjectScheduleInput(project_id=input.project_id)
        )
        return saved
