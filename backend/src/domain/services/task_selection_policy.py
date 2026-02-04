"""Task selection policy for enforcing business rules."""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from backend.src.domain.entities import (
    Project,
    ProjectMember,
    Task,
    TaskDependency,
    TaskStatus,
    Workload,
)
from backend.src.domain.entities.project_config import ProjectConfig


@dataclass
class SelectionViolation:
    """Represents a violation of task selection rules."""

    rule_id: str
    message: str


@dataclass
class SelectionContext:
    """Context required to evaluate task selection eligibility."""

    task: Task
    project: Project
    member: ProjectMember
    assigned_tasks: list[Task]
    dependencies: list[TaskDependency]
    all_project_tasks: list[Task]
    config: ProjectConfig


class TaskSelectionPolicy:
    """
    Policy object that centralizes all task selection business rules.

    This policy encapsulates:
    - BR-PROJ-002: Manager cannot select tasks
    - BR-TASK-004: Task must have difficulty points
    - BR-ASSIGN-002: Role must match (if required)
    - BR-ASSIGN-003: Workload cannot exceed Impossible threshold
    - BR-ASSIGN-004: Single-task focus (unless multitasking enabled)
    - BR-DEP-001/003: Dependencies must be satisfied

    Benefits:
    - Centralized rule enforcement
    - Easy to test individual rules
    - Rules can be reused across use cases
    - Clear separation of concerns
    """

    def evaluate(self, context: SelectionContext) -> list[SelectionViolation]:
        """
        Evaluate all selection rules and return any violations.

        Returns an empty list if task can be selected, otherwise returns
        a list of all violated rules.
        """
        violations: list[SelectionViolation] = []

        # BR-PROJ-002: Manager cannot select tasks
        if context.config.managers_cannot_select_tasks:
            violation = self._check_manager_restriction(context)
            if violation:
                violations.append(violation)

        # BR-TASK-004: Task must have difficulty points
        violation = self._check_difficulty_set(context)
        if violation:
            violations.append(violation)

        # Task must be in TODO status
        violation = self._check_task_status(context)
        if violation:
            violations.append(violation)

        # BR-ASSIGN-002: Role must match
        violation = self._check_role_match(context)
        if violation:
            violations.append(violation)

        # BR-DEP-001/003: Dependencies must be satisfied
        if context.config.enforce_dependency_blocking:
            violation = self._check_dependencies_satisfied(context)
            if violation:
                violations.append(violation)

        # BR-ASSIGN-004: Single-task focus
        if not context.config.allow_multitasking:
            violation = self._check_single_task_focus(context)
            if violation:
                violations.append(violation)

        # BR-ASSIGN-003: Workload capacity
        violation = self._check_workload_capacity(context)
        if violation:
            violations.append(violation)

        return violations

    def can_select(self, context: SelectionContext) -> bool:
        """Check if task can be selected (no violations)."""
        return len(self.evaluate(context)) == 0

    def get_first_violation(
        self, context: SelectionContext
    ) -> Optional[SelectionViolation]:
        """Get the first violation, if any (for error messages)."""
        violations = self.evaluate(context)
        return violations[0] if violations else None

    def _check_manager_restriction(
        self, context: SelectionContext
    ) -> Optional[SelectionViolation]:
        """BR-PROJ-002: Manager cannot select tasks."""
        if context.project.is_manager(context.member.user_id):
            return SelectionViolation(
                rule_id="BR-PROJ-002",
                message="Managers cannot select tasks. Their role is administrative only.",
            )
        return None

    def _check_difficulty_set(
        self, context: SelectionContext
    ) -> Optional[SelectionViolation]:
        """BR-TASK-004: Task must have difficulty points set."""
        if context.task.difficulty_points is None:
            return SelectionViolation(
                rule_id="BR-TASK-004",
                message="Task has no difficulty points set.",
            )
        return None

    def _check_task_status(
        self, context: SelectionContext
    ) -> Optional[SelectionViolation]:
        """Task must be in TODO status to be selected."""
        if context.task.status != TaskStatus.TODO:
            return SelectionViolation(
                rule_id="BR-TASK-003",
                message=f"Task is in {context.task.status.value} status, not Todo.",
            )
        return None

    def _check_role_match(
        self, context: SelectionContext
    ) -> Optional[SelectionViolation]:
        """BR-ASSIGN-002: Task role must match member's role (if specified)."""
        if (
            context.task.required_role_id is not None
            and context.task.required_role_id != context.member.role_id
        ):
            return SelectionViolation(
                rule_id="BR-ASSIGN-002",
                message="Task requires a different role.",
            )
        return None

    def _check_dependencies_satisfied(
        self, context: SelectionContext
    ) -> Optional[SelectionViolation]:
        """BR-DEP-001/003: All blocking tasks must be Done."""
        # Find all tasks that block this task
        blocking_task_ids = {
            dep.blocking_task_id
            for dep in context.dependencies
            if dep.blocked_task_id == context.task.id
        }

        if not blocking_task_ids:
            return None

        # Check if all blocking tasks are Done
        for task in context.all_project_tasks:
            if task.id in blocking_task_ids and task.status != TaskStatus.DONE:
                return SelectionViolation(
                    rule_id="BR-DEP-001",
                    message="Task has unfinished dependencies.",
                )

        return None

    def _check_single_task_focus(
        self, context: SelectionContext
    ) -> Optional[SelectionViolation]:
        """BR-ASSIGN-004: Cannot select if already working on a task (single-task focus)."""
        doing_tasks = [
            t for t in context.assigned_tasks if t.status == TaskStatus.DOING
        ]
        if doing_tasks:
            return SelectionViolation(
                rule_id="BR-ASSIGN-004",
                message="Already working on another task. Complete or abandon it first.",
            )
        return None

    def _check_workload_capacity(
        self, context: SelectionContext
    ) -> Optional[SelectionViolation]:
        """BR-ASSIGN-003: Workload cannot exceed Impossible threshold."""
        if context.task.difficulty_points is None:
            return None  # Already caught by difficulty check

        workload = Workload.from_tasks(
            context.assigned_tasks,
            context.member.seniority_level,
            context.config.base_capacity,
        )

        if not workload.can_take_additional_points(
            context.task.difficulty_points,
            context.config.max_workload_ratio,
        ):
            return SelectionViolation(
                rule_id="BR-ASSIGN-003",
                message=f"Selecting this task would exceed workload capacity "
                f"(current ratio: {workload.ratio:.2f}).",
            )
        return None
