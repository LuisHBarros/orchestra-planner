"""Add task report use case."""

from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import TaskLog, TaskStatus
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
class AddTaskReportInput:
    """Input for adding a task report."""

    task_id: UUID
    user_id: UUID  # User ID of the employee adding the report
    report_text: str  # The progress report content


class AddTaskReportUseCase:
    """
    Use case for adding a progress report to a task.

    UC-042: Add Task Report
    - Actor: Employee
    - Input: Text update (e.g., "Fixed the bug in login")
    - Outcome: Report saved.

    Reports are used to track progress on tasks. They can optionally
    be analyzed by LLM to estimate progress percentage (UC-043).
    """

    def __init__(
        self,
        project_member_repository: ProjectMemberRepository,
        task_repository: TaskRepository,
        task_log_repository: TaskLogRepository,
    ):
        self.project_member_repository = project_member_repository
        self.task_repository = task_repository
        self.task_log_repository = task_log_repository

    async def execute(self, input: AddTaskReportInput) -> TaskLog:
        """
        Add a progress report to a task.

        Only the assigned employee can add reports to their task.
        The task must be in Doing status.

        Returns the created TaskLog entry.

        Raises:
            ValueError: If report text is empty.
            TaskNotFoundError: If task doesn't exist.
            TaskNotOwnedError: If user doesn't own the task.
            ValueError: If task is not in Doing status.
        """
        # Validate report text is provided
        if not input.report_text or not input.report_text.strip():
            raise ValueError("Report text cannot be empty")

        # Find the task
        task = await self.task_repository.find_by_id(input.task_id)
        if task is None:
            raise TaskNotFoundError(str(input.task_id))

        # Verify task is in Doing status
        if task.status != TaskStatus.DOING:
            raise ValueError(
                f"Cannot add report to task with status {task.status.value}. "
                "Task must be in Doing status."
            )

        # Verify task has an assignee
        if task.assignee_id is None:
            raise TaskNotOwnedError(str(input.task_id), str(input.user_id))

        # Find the member and verify ownership
        member = await self.project_member_repository.find_by_project_and_user(
            task.project_id, input.user_id
        )
        if member is None or member.id != task.assignee_id:
            raise TaskNotOwnedError(str(input.task_id), str(input.user_id))

        # Create the report log entry
        log = TaskLog.create_report_log(
            task_id=task.id,
            author_id=member.id,
            report_text=input.report_text.strip(),
        )
        await self.task_log_repository.save(log)

        return log
