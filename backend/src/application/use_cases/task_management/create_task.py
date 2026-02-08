"""Create task use case."""

from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import Task
from backend.src.domain.errors import ManagerRequiredError, ProjectNotFoundError
from backend.src.domain.ports.repositories import ProjectRepository, TaskRepository
from backend.src.domain.ports.unit_of_work import UnitOfWork


@dataclass
class CreateTaskInput:
    """Input for creating a task."""

    project_id: UUID
    requester_id: UUID
    title: str
    description: str = ""
    difficulty_points: int | None = None
    required_role_id: UUID | None = None


class CreateTaskUseCase:
    """Use case for creating a new task in a project."""

    def __init__(
        self,
        uow: UnitOfWork | None = None,
        project_repository: ProjectRepository | None = None,
        task_repository: TaskRepository | None = None,
    ):
        self.uow = uow
        self.project_repository = project_repository
        self.task_repository = task_repository

    async def execute(self, input: CreateTaskInput) -> Task:
        """
        Create a new task in a project.

        BR-TASK-001: Only the Manager can create, edit, or delete Tasks.

        Raises:
            ProjectNotFoundError: If project doesn't exist.
            ManagerRequiredError: If requester is not the project manager.
        """
        if self.uow is not None:
            async with self.uow:
                project = await self.uow.project_repository.find_by_id(input.project_id)
                if project is None:
                    raise ProjectNotFoundError(str(input.project_id))

                if not project.is_manager(input.requester_id):
                    raise ManagerRequiredError("create task")

                task = Task(
                    project_id=project.id,
                    title=input.title,
                    description=input.description,
                    difficulty_points=input.difficulty_points,
                    required_role_id=input.required_role_id,
                )

                await self.uow.task_repository.save(task)
                await self.uow.commit()
            return task

        if self.project_repository is None or self.task_repository is None:
            raise RuntimeError("CreateTaskUseCase requires uow or repositories")
        project = await self.project_repository.find_by_id(input.project_id)
        if project is None:
            raise ProjectNotFoundError(str(input.project_id))
        if not project.is_manager(input.requester_id):
            raise ManagerRequiredError("create task")
        task = Task(
            project_id=project.id,
            title=input.title,
            description=input.description,
            difficulty_points=input.difficulty_points,
            required_role_id=input.required_role_id,
        )
        await self.task_repository.save(task)

        return task
