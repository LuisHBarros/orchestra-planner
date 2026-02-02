"""Select task use case."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from backend.src.domain.entities import Task, TaskStatus, Workload
from backend.src.domain.errors import (
    ProjectAccessDeniedError,
    ProjectNotFoundError,
    TaskNotFoundError,
    TaskNotSelectableError,
    WorkloadExceededError,
)
from backend.src.domain.ports.repositories import (
    ProjectMemberRepository,
    ProjectRepository,
    TaskRepository,
)


@dataclass
class SelectTaskInput:
    """Input for selecting a task."""

    project_id: UUID
    task_id: UUID
    user_id: UUID


class SelectTaskUseCase:
    """Use case for selecting (self-assigning) a task."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        project_member_repository: ProjectMemberRepository,
        task_repository: TaskRepository,
    ):
        self.project_repository = project_repository
        self.project_member_repository = project_member_repository
        self.task_repository = task_repository

    async def execute(self, input: SelectTaskInput) -> Task:
        """
        Select a task for work (self-assignment).

        BR-ASSIGN-001: Employees select tasks themselves.
        BR-ASSIGN-002: Only tasks matching Employee's Role can be selected.
        BR-ASSIGN-003: Cannot select if workload would exceed Impossible threshold.
        BR-TASK-004: Cannot select if difficulty is not set.

        Raises:
            ProjectNotFoundError: If project doesn't exist.
            ProjectAccessDeniedError: If user is not a project member.
            TaskNotFoundError: If task doesn't exist.
            TaskNotSelectableError: If task cannot be selected.
            WorkloadExceededError: If selecting would exceed workload limit.
        """
        project = await self.project_repository.find_by_id(input.project_id)
        if project is None:
            raise ProjectNotFoundError(str(input.project_id))

        member = await self.project_member_repository.find_by_project_and_user(
            input.project_id, input.user_id
        )
        if member is None:
            raise ProjectAccessDeniedError(str(input.user_id), str(input.project_id))

        task = await self.task_repository.find_by_id(input.task_id)
        if task is None:
            raise TaskNotFoundError(str(input.task_id))

        if task.project_id != input.project_id:
            raise TaskNotFoundError(str(input.task_id))

        # BR-TASK-004: Cannot select if difficulty is not set
        if task.difficulty_points is None:
            raise TaskNotSelectableError(
                str(input.task_id), "has no difficulty points set"
            )

        # Check task is in correct status
        if task.status != TaskStatus.TODO:
            raise TaskNotSelectableError(
                str(input.task_id), f"is in {task.status.value} status"
            )

        # BR-ASSIGN-002: Check role match if task requires specific role
        if (
            task.required_role_id is not None
            and task.required_role_id != member.role_id
        ):
            raise TaskNotSelectableError(
                str(input.task_id), "requires a different role"
            )

        # BR-ASSIGN-003: Check workload capacity
        current_tasks = await self.task_repository.find_by_assignee(member.id)
        current_points = [
            t.difficulty_points
            for t in current_tasks
            if t.status == TaskStatus.DOING and t.difficulty_points is not None
        ]
        workload = Workload.calculate(current_points, member.seniority_level)

        if not workload.can_take_additional_points(task.difficulty_points):
            raise WorkloadExceededError(float(workload.ratio))

        # Select the task
        task.select(member.id)
        await self.task_repository.save(task)

        return task
