"""Remove from task use case."""

from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import Task, TaskLog, TaskStatus
from backend.src.domain.errors import (
    ManagerRequiredError,
    ProjectNotFoundError,
    TaskNotAssignedError,
    TaskNotFoundError,
)
from backend.src.domain.ports.repositories import (
    ProjectMemberRepository,
    ProjectRepository,
    TaskLogRepository,
    TaskRepository,
)


@dataclass
class RemoveFromTaskInput:
    """Input for removing an employee from a task."""

    task_id: UUID
    manager_user_id: UUID  # User ID of the manager performing the action


class RemoveFromTaskUseCase:
    """
    Use case for forcibly removing an employee from a task.

    UC-050: Remove from Task (Force)
    - Actor: Manager
    - Input: Task ID
    - Outcome: Task returns to Todo. Considered "Fired from Task".

    This allows a manager to unassign a task from an employee,
    returning it to the Todo pool for someone else to pick up.
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
        project_member_repository: ProjectMemberRepository,
        task_repository: TaskRepository,
        task_log_repository: TaskLogRepository,
    ):
        self.project_repository = project_repository
        self.project_member_repository = project_member_repository
        self.task_repository = task_repository
        self.task_log_repository = task_log_repository

    async def execute(self, input: RemoveFromTaskInput) -> Task:
        """
        Remove an employee from a task (force unassign).

        BR-ASSIGN-005: All un-assignments are logged in history for auditing.

        Returns the updated task.

        Raises:
            TaskNotFoundError: If task doesn't exist.
            ProjectNotFoundError: If project doesn't exist.
            ManagerRequiredError: If user is not the project manager.
            TaskNotAssignedError: If task is not assigned to anyone.
            ValueError: If task is not in Doing status.
        """
        # Find the task
        task = await self.task_repository.find_by_id(input.task_id)
        if task is None:
            raise TaskNotFoundError(str(input.task_id))

        # Verify project exists and user is manager
        project = await self.project_repository.find_by_id(task.project_id)
        if project is None:
            raise ProjectNotFoundError(str(task.project_id))

        if not project.is_manager(input.manager_user_id):
            raise ManagerRequiredError("remove employee from task")

        # Verify task is assigned
        if task.assignee_id is None:
            raise TaskNotAssignedError(str(input.task_id))

        # Verify task is in Doing status
        if task.status != TaskStatus.DOING:
            raise ValueError(
                f"Cannot remove from task with status {task.status.value}. "
                "Task must be in Doing status."
            )

        # Get the manager's member record for audit attribution
        # Manager may or may not be a ProjectMember, so we use their user_id directly
        # if they don't have a member record
        manager_member = await self.project_member_repository.find_by_project_and_user(
            task.project_id, input.manager_user_id
        )

        # Store the previous assignee for the log content
        previous_assignee_id = task.assignee_id

        # Abandon the task (returns to Todo, unassigns)
        task.abandon()
        await self.task_repository.save(task)

        # Create audit log (BR-ASSIGN-005)
        # Use UNASSIGN type since this is a forced removal by manager
        # Author is the manager who performed the action, not the removed employee
        log = TaskLog.create_unassignment_log(
            task_id=task.id,
            author_id=manager_member.id if manager_member else previous_assignee_id,
            content=f"Forcibly removed from task by manager (previous assignee: {previous_assignee_id})",
        )
        await self.task_log_repository.save(log)

        return task
