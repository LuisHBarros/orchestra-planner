"""Abandon task use case."""

from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import Task
from backend.src.domain.errors import (
    TaskNotFoundError,
    TaskNotOwnedError,
)
from backend.src.domain.ports.repositories import (
    ProjectMemberRepository,
    TaskRepository,
)


@dataclass
class AbandonTaskInput:
    """Input for abandoning a task."""

    task_id: UUID
    user_id: UUID


class AbandonTaskUseCase:
    """Use case for abandoning a task."""

    def __init__(
        self,
        project_member_repository: ProjectMemberRepository,
        task_repository: TaskRepository,
    ):
        self.project_member_repository = project_member_repository
        self.task_repository = task_repository

    async def execute(self, input: AbandonTaskInput) -> Task:
        """
        Abandon a task that the user is working on.

        The task returns to Todo status and becomes unassigned.
        Only the assigned user can abandon their own task.

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

        task.abandon()
        await self.task_repository.save(task)

        return task
