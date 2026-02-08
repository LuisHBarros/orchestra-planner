"""Fire employee use case."""

from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import Task, TaskStatus
from backend.src.domain.errors import (
    ManagerRequiredError,
    ProjectNotFoundError,
)
from backend.src.domain.ports.unit_of_work import UnitOfWork


@dataclass
class FireEmployeeInput:
    """Input for firing an employee from a project."""

    project_id: UUID
    employee_user_id: UUID  # User ID of the employee to fire
    manager_user_id: UUID  # User ID of the manager performing the action


class MemberNotFoundError(Exception):
    """Raised when project member is not found."""

    def __init__(self, user_id: str, project_id: str):
        self.user_id = user_id
        self.project_id = project_id
        super().__init__(f"User {user_id} is not a member of project {project_id}")


class FireEmployeeUseCase:
    """
    Use case for firing an employee from a project.

    UC-051: Fire Employee
    - Actor: Manager
    - Input: Employee ID
    - Outcome: Employee removed from Project. All their active tasks return to Todo.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, input: FireEmployeeInput) -> list[Task]:
        """
        Fire an employee from a project.

        Returns the list of tasks that were unassigned.

        Raises:
            ProjectNotFoundError: If project doesn't exist.
            ManagerRequiredError: If user is not the project manager.
            MemberNotFoundError: If employee is not a member of the project.
        """
        async with self.uow:
            # Verify project exists
            project = await self.uow.project_repository.find_by_id(input.project_id)
            if project is None:
                raise ProjectNotFoundError(str(input.project_id))

            # Verify requester is the manager
            if not project.is_manager(input.manager_user_id):
                raise ManagerRequiredError("fire employee")

            # Find the employee's membership
            member = await self.uow.project_member_repository.find_by_project_and_user(
                input.project_id, input.employee_user_id
            )
            if member is None:
                raise MemberNotFoundError(
                    str(input.employee_user_id), str(input.project_id)
                )

            # Cannot fire the manager
            if project.is_manager(input.employee_user_id):
                raise ValueError("Cannot fire the project manager")

            # Find all tasks assigned to this member and unassign them
            all_tasks = await self.uow.task_repository.find_by_project(input.project_id)
            affected_tasks: list[Task] = []

            for task in all_tasks:
                if task.assignee_id == member.id and task.status == TaskStatus.DOING:
                    task.abandon()
                    affected_tasks.append(task)

            # Save all affected tasks
            if affected_tasks:
                await self.uow.task_repository.save_many(affected_tasks)

            # Remove the member from the project
            await self.uow.project_member_repository.delete(member.id)

            await self.uow.commit()

        return affected_tasks
