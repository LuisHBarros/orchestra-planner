"""Complete task use case."""

from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import Task, TaskLog
from backend.src.domain.errors import (
    TaskNotFoundError,
    TaskNotOwnedError,
)
from backend.src.domain.ports.repositories import (
    ProjectMemberRepository,
    TaskLogRepository,
    TaskRepository,
)


@dataclass
class CompleteTaskInput:
    """Input for completing a task."""

    task_id: UUID
    user_id: UUID


class CompleteTaskUseCase:
    """Use case for completing a task."""

    def __init__(
        self,
        project_member_repository: ProjectMemberRepository,
        task_repository: TaskRepository,
        task_log_repository: TaskLogRepository,
    ):
        self.project_member_repository = project_member_repository
        self.task_repository = task_repository
        self.task_log_repository = task_log_repository

    async def execute(self, input: CompleteTaskInput) -> Task:
        """
        Complete a task that the user is working on.

        BR-ASSIGN-005: All status changes are logged in history.

        Only the assigned user can complete their own task.

        Raises:
            TaskNotFoundError: If task doesn't exist.
            TaskNotOwnedError: If user doesn't own the task.
            ValueError: If task is not in Doing status.
        """
        task = await self.task_repository.find_by_id(input.task_id)
        if task is None:
            raise TaskNotFoundError(str(input.task_id))

        # Find the member to verify ownership
        if task.assignee_id is None:
            raise TaskNotOwnedError(str(input.task_id), str(input.user_id))

        member = await self.project_member_repository.find_by_project_and_user(
            task.project_id, input.user_id
        )
        if member is None or member.id != task.assignee_id:
            raise TaskNotOwnedError(str(input.task_id), str(input.user_id))

        old_status = task.status.value
        task.complete()
        await self.task_repository.save(task)

        # Create audit log (BR-ASSIGN-005)
        log = TaskLog.create_status_change_log(
            task_id=task.id,
            author_id=member.id,
            old_status=old_status,
            new_status=task.status.value,
        )
        await self.task_log_repository.save(log)

        return task
