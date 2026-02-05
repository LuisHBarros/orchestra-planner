"""Select task use case."""

from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import ProjectConfig, Task, TaskLog
from backend.src.domain.errors import (
    ManagerRequiredError,
    ProjectAccessDeniedError,
    ProjectNotFoundError,
    TaskNotFoundError,
    TaskNotSelectableError,
    WorkloadExceededError,
)
from backend.src.domain.ports.repositories import (
    ProjectMemberRepository,
    ProjectRepository,
    TaskDependencyRepository,
    TaskLogRepository,
    TaskRepository,
)
from backend.src.domain.services.task_selection_policy import (
    SelectionContext,
    TaskSelectionPolicy,
)


@dataclass
class SelectTaskInput:
    """Input for selecting a task."""

    project_id: UUID
    task_id: UUID
    user_id: UUID


class SelectTaskUseCase:
    """
    Use case for selecting (self-assigning) a task.

    Uses TaskSelectionPolicy to enforce all business rules:
    - BR-PROJ-002: Manager cannot select tasks
    - BR-TASK-004: Task must have difficulty points
    - BR-ASSIGN-002: Role must match (if required)
    - BR-ASSIGN-003: Workload cannot exceed Impossible threshold
    - BR-ASSIGN-004: Single-task focus (unless multitasking enabled)
    - BR-DEP-001/003: Dependencies must be satisfied
    - BR-ASSIGN-005: All assignments are logged
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
        project_member_repository: ProjectMemberRepository,
        task_repository: TaskRepository,
        task_log_repository: TaskLogRepository,
        task_dependency_repository: TaskDependencyRepository,
        selection_policy: TaskSelectionPolicy | None = None,
        config: ProjectConfig | None = None,
    ):
        self.project_repository = project_repository
        self.project_member_repository = project_member_repository
        self.task_repository = task_repository
        self.task_log_repository = task_log_repository
        self.task_dependency_repository = task_dependency_repository
        self.selection_policy = selection_policy or TaskSelectionPolicy()
        self.config = config or ProjectConfig.default()

    async def execute(self, input: SelectTaskInput) -> Task:
        """
        Select a task for work (self-assignment).

        Raises:
            ProjectNotFoundError: If project doesn't exist.
            ProjectAccessDeniedError: If user is not a project member.
            TaskNotFoundError: If task doesn't exist.
            ManagerRequiredError: If user is manager (BR-PROJ-002).
            TaskNotSelectableError: If task cannot be selected.
            WorkloadExceededError: If selecting would exceed workload limit.
        """
        # Fetch project
        project = await self.project_repository.find_by_id(input.project_id)
        if project is None:
            raise ProjectNotFoundError(str(input.project_id))

        # Fetch member
        member = await self.project_member_repository.find_by_project_and_user(
            input.project_id, input.user_id
        )
        if member is None:
            raise ProjectAccessDeniedError(str(input.user_id), str(input.project_id))

        # Fetch task
        task = await self.task_repository.find_by_id(input.task_id)
        if task is None:
            raise TaskNotFoundError(str(input.task_id))

        if task.project_id != input.project_id:
            raise TaskNotFoundError(str(input.task_id))

        # Fetch context for policy evaluation
        assigned_tasks = await self.task_repository.find_by_assignee(member.id)
        dependencies = await self.task_dependency_repository.find_by_project(
            input.project_id
        )
        all_project_tasks = await self.task_repository.find_by_project(input.project_id)

        # Build selection context
        context = SelectionContext(
            task=task,
            project=project,
            member=member,
            assigned_tasks=assigned_tasks,
            dependencies=dependencies,
            all_project_tasks=all_project_tasks,
            config=self.config,
        )

        # Evaluate selection policy
        violation = self.selection_policy.get_first_violation(context)
        if violation:
            self._raise_appropriate_error(violation, task, input)

        # Select the task
        task.select(member.id)
        await self.task_repository.save(task)

        # Create audit log (BR-ASSIGN-005)
        log = TaskLog.create_assignment_log(
            task_id=task.id,
            author_id=member.id,
        )
        await self.task_log_repository.save(log)

        return task

    def _raise_appropriate_error(
        self,
        violation,
        task: Task,
        input: SelectTaskInput,
    ) -> None:
        """Map policy violations to appropriate domain errors."""
        rule_id = violation.rule_id

        if rule_id == "BR-PROJ-002":
            raise ManagerRequiredError("Managers cannot select tasks (BR-PROJ-002)")
        elif rule_id == "BR-ASSIGN-003":
            # Extract ratio from violation message (format: "... (current ratio: X.XX).")
            ratio = self._extract_ratio_from_message(violation.message)
            raise WorkloadExceededError(ratio)
        elif rule_id in (
            "BR-TASK-004",
            "BR-TASK-003",
            "BR-ASSIGN-002",
            "BR-DEP-001",
            "BR-ASSIGN-004",
        ):
            raise TaskNotSelectableError(str(input.task_id), violation.message)
        else:
            raise TaskNotSelectableError(str(input.task_id), violation.message)

    def _extract_ratio_from_message(self, message: str) -> float:
        """Extract workload ratio from violation message."""
        import re

        match = re.search(r"current ratio: (\d+\.?\d*)", message)
        if match:
            return float(match.group(1))
        return 0.0
