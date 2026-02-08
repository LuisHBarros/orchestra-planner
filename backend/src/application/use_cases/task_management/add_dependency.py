"""Add task dependency use case."""

from dataclasses import dataclass
from uuid import UUID

from backend.src.application.use_cases.project_management.recalculate_project_schedule import (
    RecalculateProjectScheduleInput,
    RecalculateProjectScheduleUseCase,
)
from backend.src.domain.entities import TaskDependency, TaskStatus, detect_circular_dependency
from backend.src.domain.errors import (
    CircularDependencyError,
    ManagerRequiredError,
    ProjectNotFoundError,
    TaskNotFoundError,
)
from backend.src.domain.ports.unit_of_work import UnitOfWork


@dataclass
class AddDependencyInput:
    """Input for adding a task dependency."""

    project_id: UUID
    blocking_task_id: UUID
    blocked_task_id: UUID
    manager_user_id: UUID


class AddDependencyUseCase:
    """Add a finish-to-start dependency between tasks."""

    def __init__(
        self,
        uow: UnitOfWork,
        recalculate_schedule_use_case: RecalculateProjectScheduleUseCase,
    ):
        self.uow = uow
        self.recalculate_schedule_use_case = recalculate_schedule_use_case

    async def execute(self, input: AddDependencyInput) -> TaskDependency:
        dependency = TaskDependency(
            blocking_task_id=input.blocking_task_id,
            blocked_task_id=input.blocked_task_id,
        )

        async with self.uow:
            project = await self.uow.project_repository.find_by_id(input.project_id)
            if project is None:
                raise ProjectNotFoundError(str(input.project_id))

            if not project.is_manager(input.manager_user_id):
                raise ManagerRequiredError("add dependency")

            blocking_task = await self.uow.task_repository.find_by_id(
                input.blocking_task_id
            )
            blocked_task = await self.uow.task_repository.find_by_id(input.blocked_task_id)
            if (
                blocking_task is None
                or blocked_task is None
                or blocking_task.project_id != input.project_id
                or blocked_task.project_id != input.project_id
            ):
                raise TaskNotFoundError(
                    f"{input.blocking_task_id}->{input.blocked_task_id}"
                )

            existing = await self.uow.task_dependency_repository.find_by_project(
                input.project_id
            )
            if detect_circular_dependency(dependency, existing):
                raise CircularDependencyError(
                    str(input.blocking_task_id), str(input.blocked_task_id)
                )

            existing_pair = await self.uow.task_dependency_repository.find_by_tasks(
                input.blocking_task_id,
                input.blocked_task_id,
            )
            if existing_pair is not None:
                raise ValueError("Dependency already exists")

            await self.uow.task_dependency_repository.save(dependency)

            if blocking_task.status != TaskStatus.DONE and blocked_task.status in {
                TaskStatus.TODO,
                TaskStatus.DOING,
            }:
                blocked_task.block()
                await self.uow.task_repository.save(blocked_task)

            await self.uow.commit()

        await self.recalculate_schedule_use_case.execute(
            RecalculateProjectScheduleInput(project_id=input.project_id)
        )

        return dependency
