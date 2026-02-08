"""Recalculate project schedule use case.

Trigger this after:
- Task creation or deletion
- Dependency changes (add/remove)
- Assignment changes (task assignee_id)
"""

from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import SeniorityLevel, Task, TaskStatus
from backend.src.domain.ports.repositories import (
    ProjectRepository,
    ProjectMemberRepository,
    TaskDependencyRepository,
    TaskRepository,
)
from backend.src.domain.services.schedule_calculator import (
    ProjectSchedule,
    ScheduleCalculator,
)


@dataclass
class RecalculateProjectScheduleInput:
    """Input for recalculating project schedule."""

    project_id: UUID
    default_seniority: SeniorityLevel = SeniorityLevel.MID


class RecalculateProjectScheduleUseCase:
    """Use case for recalculating project schedule and persisting task dates."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        task_repository: TaskRepository,
        task_dependency_repository: TaskDependencyRepository,
        project_member_repository: ProjectMemberRepository,
        schedule_calculator: ScheduleCalculator,
    ):
        self.project_repository = project_repository
        self.task_repository = task_repository
        self.task_dependency_repository = task_dependency_repository
        self.project_member_repository = project_member_repository
        self.schedule_calculator = schedule_calculator

    async def execute(self, input: RecalculateProjectScheduleInput) -> ProjectSchedule:
        """
        Recalculate schedule for all tasks in the project and persist dates.

        BR-SCHED-003: Schedule is recalculated when dependencies change.
        Uses member seniority for assigned tasks; default_seniority for unassigned.
        """
        tasks = await self.task_repository.find_by_project(input.project_id)
        deps = await self.task_dependency_repository.find_by_project(input.project_id)
        members = await self.project_member_repository.find_by_project(input.project_id)
        project = await self.project_repository.find_by_id(input.project_id)
        working_calendar = project.calendar if project else None

        # Build member lookup: member_id -> seniority (for assignee duration)
        member_seniority = {m.id: m.seniority_level for m in members}

        # Per-task assignee seniority (task_id -> SeniorityLevel)
        assignee_seniority = {
            t.id: member_seniority.get(t.assignee_id, input.default_seniority)
            for t in tasks
        }

        schedule = self.schedule_calculator.calculate_schedule(
            tasks=tasks,
            dependencies=deps,
            assignee_seniority=assignee_seniority,
            working_calendar=working_calendar,
        )

        # Update tasks with calculated dates
        # BR-SCHED-005: For in-progress tasks, only update end date (not start date)
        tasks_to_save: list[Task] = []
        for task in tasks:
            if task.id in schedule.task_schedules:
                sched = schedule.task_schedules[task.id]
                if task.status == TaskStatus.DOING:
                    # Only update end date for in-progress tasks
                    task.update_schedule(
                        expected_start_date=None,
                        expected_end_date=sched.expected_end_date,
                    )
                else:
                    task.update_schedule(
                        sched.expected_start_date, sched.expected_end_date
                    )
                tasks_to_save.append(task)

        if tasks_to_save:
            await self.task_repository.save_many(tasks_to_save)

        return schedule
