"""Delete task use case."""

from dataclasses import dataclass
from uuid import UUID

from backend.src.application.use_cases.project_management.recalculate_project_schedule import (
    RecalculateProjectScheduleInput,
    RecalculateProjectScheduleUseCase,
)
from backend.src.domain.errors import ManagerRequiredError, ProjectNotFoundError, TaskNotFoundError
from backend.src.domain.ports.unit_of_work import UnitOfWork


@dataclass
class DeleteTaskInput:
    """Input for deleting a task."""

    project_id: UUID
    task_id: UUID
    manager_user_id: UUID


class DeleteTaskUseCase:
    """Delete a task and dependencies pointing to it."""

    def __init__(
        self,
        uow: UnitOfWork,
        recalculate_schedule_use_case: RecalculateProjectScheduleUseCase,
    ):
        self.uow = uow
        self.recalculate_schedule_use_case = recalculate_schedule_use_case

    async def execute(self, input: DeleteTaskInput) -> None:
        async with self.uow:
            project = await self.uow.project_repository.find_by_id(input.project_id)
            if project is None:
                raise ProjectNotFoundError(str(input.project_id))

            if not project.is_manager(input.manager_user_id):
                raise ManagerRequiredError("delete task")

            task = await self.uow.task_repository.find_by_id(input.task_id)
            if task is None or task.project_id != input.project_id:
                raise TaskNotFoundError(str(input.task_id))

            await self.uow.task_dependency_repository.delete(input.task_id)
            await self.uow.task_repository.delete(input.task_id)
            await self.uow.commit()

        await self.recalculate_schedule_use_case.execute(
            RecalculateProjectScheduleInput(project_id=input.project_id)
        )
