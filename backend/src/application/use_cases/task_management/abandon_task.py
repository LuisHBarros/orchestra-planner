"""Abandon task use case."""

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
class AbandonTaskInput:
    """Input for abandoning a task."""

    task_id: UUID
    user_id: UUID
    reason: str  # BR-ABANDON-002: Reason is required


class AbandonTaskUseCase:
    """Use case for abandoning a task."""

    def __init__(
        self,
        project_member_repository: ProjectMemberRepository,
        task_repository: TaskRepository,
        task_log_repository: TaskLogRepository,
    ):
        self.project_member_repository = project_member_repository
        self.task_repository = task_repository
        self.task_log_repository = task_log_repository

    async def execute(self, input: AbandonTaskInput) -> Task:
        """
        Abandon a task that the user is working on.

        BR-ABANDON-002: The user must provide a reason for abandonment.
        BR-ASSIGN-005: All un-assignments are logged in history.

        The task returns to Todo status and becomes unassigned.
        Only the assigned user can abandon their own task.

        Raises:
            TaskNotFoundError: If task doesn't exist.
            TaskNotOwnedError: If user doesn't own the task.
            ValueError: If task is not in Doing status or reason is empty.
        """
        # Validate reason is provided (BR-ABANDON-002)
        if not input.reason or not input.reason.strip():
            raise ValueError("Abandonment reason is required (BR-ABANDON-002)")

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

        # Abandon the task
        task.abandon()
        await self.task_repository.save(task)

        # Create audit log (BR-ABANDON-002, BR-ASSIGN-005)
        log = TaskLog.create_abandon_log(
            task_id=task.id,
            author_id=member.id,
            reason=input.reason,
        )
        await self.task_log_repository.save(log)

        return task
