"""Resign from project use case."""

from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import Task, TaskStatus
from backend.src.domain.errors import (
    ProjectNotFoundError,
)
from backend.src.domain.ports.repositories import (
    ProjectMemberRepository,
    ProjectRepository,
    TaskRepository,
)


@dataclass
class ResignFromProjectInput:
    """Input for resigning from a project."""

    project_id: UUID
    user_id: UUID  # User ID of the employee resigning


class MemberNotFoundError(Exception):
    """Raised when project member is not found."""

    def __init__(self, user_id: str, project_id: str):
        self.user_id = user_id
        self.project_id = project_id
        super().__init__(f"User {user_id} is not a member of project {project_id}")


class ManagerCannotResignError(Exception):
    """Raised when manager tries to resign from their own project."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        super().__init__(
            f"Manager cannot resign from project {project_id}. "
            "Transfer ownership or delete the project instead."
        )


class ResignFromProjectUseCase:
    """
    Use case for an employee to resign from a project.

    UC-052: Resign from Project
    - Actor: Employee
    - Outcome: Employee removed. Active tasks return to Todo.
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
        project_member_repository: ProjectMemberRepository,
        task_repository: TaskRepository,
    ):
        self.project_repository = project_repository
        self.project_member_repository = project_member_repository
        self.task_repository = task_repository

    async def execute(self, input: ResignFromProjectInput) -> list[Task]:
        """
        Resign from a project.

        Returns the list of tasks that were unassigned.

        Raises:
            ProjectNotFoundError: If project doesn't exist.
            MemberNotFoundError: If user is not a member of the project.
            ManagerCannotResignError: If user is the project manager.
        """
        # Verify project exists
        project = await self.project_repository.find_by_id(input.project_id)
        if project is None:
            raise ProjectNotFoundError(str(input.project_id))

        # Manager cannot resign (they own the project)
        if project.is_manager(input.user_id):
            raise ManagerCannotResignError(str(input.project_id))

        # Find the employee's membership
        member = await self.project_member_repository.find_by_project_and_user(
            input.project_id, input.user_id
        )
        if member is None:
            raise MemberNotFoundError(str(input.user_id), str(input.project_id))

        # Find all tasks assigned to this member and unassign them
        all_tasks = await self.task_repository.find_by_project(input.project_id)
        affected_tasks: list[Task] = []

        for task in all_tasks:
            if task.assignee_id == member.id and task.status == TaskStatus.DOING:
                task.abandon()
                affected_tasks.append(task)

        # Save all affected tasks
        if affected_tasks:
            await self.task_repository.save_many(affected_tasks)

        # Remove the member from the project
        await self.project_member_repository.delete(member.id)

        return affected_tasks
