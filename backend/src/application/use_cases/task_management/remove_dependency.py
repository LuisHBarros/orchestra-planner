"""Remove task dependency use case."""

from dataclasses import dataclass
from uuid import UUID

from backend.src.application.use_cases.project_management.recalculate_project_schedule import (
    RecalculateProjectScheduleInput,
    RecalculateProjectScheduleUseCase,
)
from backend.src.domain.entities import Task, TaskStatus
from backend.src.domain.errors import ManagerRequiredError, ProjectNotFoundError, TaskNotFoundError
from backend.src.domain.ports.unit_of_work import UnitOfWork


@dataclass
class RemoveDependencyInput:
    """Input for removing a task dependency."""

    project_id: UUID
    blocking_task_id: UUID
    blocked_task_id: UUID
    manager_user_id: UUID


class RemoveDependencyUseCase:
    """Remove a finish-to-start dependency between tasks."""

    def __init__(
        self,
        uow: UnitOfWork,
        recalculate_schedule_use_case: RecalculateProjectScheduleUseCase,
    ):
        self.uow = uow
        self.recalculate_schedule_use_case = recalculate_schedule_use_case

    async def execute(self, input: RemoveDependencyInput) -> Task:
        async with self.uow:
            project = await self.uow.project_repository.find_by_id(input.project_id)
            if project is None:
                raise ProjectNotFoundError(str(input.project_id))

            if not project.is_manager(input.manager_user_id):
                raise ManagerRequiredError("remove dependency")

            blocked_task = await self.uow.task_repository.find_by_id(input.blocked_task_id)
            if blocked_task is None or blocked_task.project_id != input.project_id:
                raise TaskNotFoundError(str(input.blocked_task_id))

            dependency = await self.uow.task_dependency_repository.find_by_tasks(
                input.blocking_task_id,
                input.blocked_task_id,
            )
            if dependency is None:
                raise TaskNotFoundError(
                    f"dependency {input.blocking_task_id}->{input.blocked_task_id}"
                )

            await self.uow.task_dependency_repository.delete_by_tasks(
                input.blocking_task_id,
                input.blocked_task_id,
            )

            if blocked_task.status == TaskStatus.BLOCKED:
                dependencies = await self.uow.task_dependency_repository.find_by_project(
                    input.project_id
                )
                remaining_blockers = {
                    dep.blocking_task_id
                    for dep in dependencies
                    if dep.blocked_task_id == input.blocked_task_id
                }

                if not remaining_blockers:
                    blocked_task.unblock()
                    await self.uow.task_repository.save(blocked_task)
                else:
                    tasks = await self.uow.task_repository.find_by_project(input.project_id)
                    task_by_id = {task.id: task for task in tasks}
                    has_open_blocker = any(
                        task_by_id.get(blocker_id)
                        and task_by_id[blocker_id].status != TaskStatus.DONE
                        for blocker_id in remaining_blockers
                    )
                    if not has_open_blocker:
                        blocked_task.unblock()
                        await self.uow.task_repository.save(blocked_task)

            await self.uow.commit()

        await self.recalculate_schedule_use_case.execute(
            RecalculateProjectScheduleInput(project_id=input.project_id)
        )

        return blocked_task
