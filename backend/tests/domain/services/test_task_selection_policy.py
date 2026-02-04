"""Tests for TaskSelectionPolicy."""

from decimal import Decimal
from uuid import uuid4

import pytest

from backend.src.domain.entities import (
    Project,
    ProjectConfig,
    ProjectMember,
    SeniorityLevel,
    Task,
    TaskDependency,
    TaskStatus,
)
from backend.src.domain.services.task_selection_policy import (
    SelectionContext,
    TaskSelectionPolicy,
)


@pytest.fixture
def policy():
    return TaskSelectionPolicy()


@pytest.fixture
def default_config():
    return ProjectConfig.default()


@pytest.fixture
def multitasking_config():
    return ProjectConfig(allow_multitasking=True)


@pytest.fixture
def manager_user_id():
    return uuid4()


@pytest.fixture
def employee_user_id():
    return uuid4()


@pytest.fixture
def project(manager_user_id):
    return Project(
        name="Test Project",
        manager_id=manager_user_id,
    )


@pytest.fixture
def role_id():
    return uuid4()


@pytest.fixture
def employee_member(project, employee_user_id, role_id):
    return ProjectMember(
        project_id=project.id,
        user_id=employee_user_id,
        role_id=role_id,
        seniority_level=SeniorityLevel.MID,
    )


@pytest.fixture
def manager_member(project, manager_user_id, role_id):
    return ProjectMember(
        project_id=project.id,
        user_id=manager_user_id,
        role_id=role_id,
        seniority_level=SeniorityLevel.LEAD,
    )


@pytest.fixture
def selectable_task(project, role_id):
    return Task(
        project_id=project.id,
        title="Selectable Task",
        difficulty_points=5,
        required_role_id=role_id,
    )


@pytest.fixture
def task_without_difficulty(project):
    return Task(
        project_id=project.id,
        title="No Difficulty Task",
    )


@pytest.fixture
def doing_task(project, employee_member):
    task = Task(
        project_id=project.id,
        title="Already Doing Task",
        difficulty_points=3,
    )
    task.select(employee_member.id)
    return task


class TestTaskSelectionPolicyManagerRestriction:
    """Tests for BR-PROJ-002: Manager cannot select tasks."""

    def test_manager_cannot_select_task(
        self,
        policy,
        default_config,
        project,
        manager_member,
        selectable_task,
    ):
        """Manager should be blocked from selecting tasks."""
        context = SelectionContext(
            task=selectable_task,
            project=project,
            member=manager_member,
            assigned_tasks=[],
            dependencies=[],
            all_project_tasks=[selectable_task],
            config=default_config,
        )

        violations = policy.evaluate(context)

        assert len(violations) >= 1
        rule_ids = [v.rule_id for v in violations]
        assert "BR-PROJ-002" in rule_ids

    def test_employee_can_select_task(
        self,
        policy,
        default_config,
        project,
        employee_member,
        selectable_task,
    ):
        """Employee should be able to select task."""
        context = SelectionContext(
            task=selectable_task,
            project=project,
            member=employee_member,
            assigned_tasks=[],
            dependencies=[],
            all_project_tasks=[selectable_task],
            config=default_config,
        )

        violations = policy.evaluate(context)

        assert len(violations) == 0

    def test_manager_restriction_can_be_disabled(
        self,
        policy,
        project,
        manager_member,
        selectable_task,
    ):
        """Manager restriction can be disabled via config."""
        config = ProjectConfig(managers_cannot_select_tasks=False)
        context = SelectionContext(
            task=selectable_task,
            project=project,
            member=manager_member,
            assigned_tasks=[],
            dependencies=[],
            all_project_tasks=[selectable_task],
            config=config,
        )

        violations = policy.evaluate(context)
        rule_ids = [v.rule_id for v in violations]

        assert "BR-PROJ-002" not in rule_ids


class TestTaskSelectionPolicyDifficultyCheck:
    """Tests for BR-TASK-004: Task must have difficulty points."""

    def test_task_without_difficulty_cannot_be_selected(
        self,
        policy,
        default_config,
        project,
        employee_member,
        task_without_difficulty,
    ):
        """Task without difficulty points should be blocked."""
        context = SelectionContext(
            task=task_without_difficulty,
            project=project,
            member=employee_member,
            assigned_tasks=[],
            dependencies=[],
            all_project_tasks=[task_without_difficulty],
            config=default_config,
        )

        violations = policy.evaluate(context)
        rule_ids = [v.rule_id for v in violations]

        assert "BR-TASK-004" in rule_ids


class TestTaskSelectionPolicyDependencies:
    """Tests for BR-DEP-001/003: Dependencies must be satisfied."""

    def test_task_with_unfinished_dependency_blocked(
        self,
        policy,
        default_config,
        project,
        employee_member,
    ):
        """Task with unfinished dependency should be blocked."""
        blocking_task = Task(
            project_id=project.id,
            title="Blocking Task",
            difficulty_points=3,
        )  # Status is TODO (not DONE)

        blocked_task = Task(
            project_id=project.id,
            title="Blocked Task",
            difficulty_points=5,
        )

        dependency = TaskDependency(
            blocking_task_id=blocking_task.id,
            blocked_task_id=blocked_task.id,
        )

        context = SelectionContext(
            task=blocked_task,
            project=project,
            member=employee_member,
            assigned_tasks=[],
            dependencies=[dependency],
            all_project_tasks=[blocking_task, blocked_task],
            config=default_config,
        )

        violations = policy.evaluate(context)
        rule_ids = [v.rule_id for v in violations]

        assert "BR-DEP-001" in rule_ids

    def test_task_with_finished_dependency_allowed(
        self,
        policy,
        default_config,
        project,
        employee_member,
    ):
        """Task with finished dependency should be allowed."""
        blocking_task = Task(
            project_id=project.id,
            title="Blocking Task",
            difficulty_points=3,
        )
        blocking_task.select(uuid4())  # Move to DOING
        blocking_task.complete()  # Move to DONE

        blocked_task = Task(
            project_id=project.id,
            title="Blocked Task",
            difficulty_points=5,
        )

        dependency = TaskDependency(
            blocking_task_id=blocking_task.id,
            blocked_task_id=blocked_task.id,
        )

        context = SelectionContext(
            task=blocked_task,
            project=project,
            member=employee_member,
            assigned_tasks=[],
            dependencies=[dependency],
            all_project_tasks=[blocking_task, blocked_task],
            config=default_config,
        )

        violations = policy.evaluate(context)
        rule_ids = [v.rule_id for v in violations]

        assert "BR-DEP-001" not in rule_ids

    def test_dependency_check_can_be_disabled(
        self,
        policy,
        project,
        employee_member,
    ):
        """Dependency check can be disabled via config."""
        blocking_task = Task(
            project_id=project.id,
            title="Blocking Task",
            difficulty_points=3,
        )

        blocked_task = Task(
            project_id=project.id,
            title="Blocked Task",
            difficulty_points=5,
        )

        dependency = TaskDependency(
            blocking_task_id=blocking_task.id,
            blocked_task_id=blocked_task.id,
        )

        config = ProjectConfig(enforce_dependency_blocking=False)

        context = SelectionContext(
            task=blocked_task,
            project=project,
            member=employee_member,
            assigned_tasks=[],
            dependencies=[dependency],
            all_project_tasks=[blocking_task, blocked_task],
            config=config,
        )

        violations = policy.evaluate(context)
        rule_ids = [v.rule_id for v in violations]

        assert "BR-DEP-001" not in rule_ids


class TestTaskSelectionPolicySingleTaskFocus:
    """Tests for BR-ASSIGN-004: Single-task focus."""

    def test_cannot_select_when_already_doing_task(
        self,
        policy,
        default_config,
        project,
        employee_member,
        selectable_task,
        doing_task,
    ):
        """Cannot select new task when already working on one."""
        context = SelectionContext(
            task=selectable_task,
            project=project,
            member=employee_member,
            assigned_tasks=[doing_task],
            dependencies=[],
            all_project_tasks=[selectable_task, doing_task],
            config=default_config,
        )

        violations = policy.evaluate(context)
        rule_ids = [v.rule_id for v in violations]

        assert "BR-ASSIGN-004" in rule_ids

    def test_can_select_when_multitasking_enabled(
        self,
        policy,
        multitasking_config,
        project,
        employee_member,
        selectable_task,
        doing_task,
    ):
        """Can select new task when multitasking is enabled."""
        context = SelectionContext(
            task=selectable_task,
            project=project,
            member=employee_member,
            assigned_tasks=[doing_task],
            dependencies=[],
            all_project_tasks=[selectable_task, doing_task],
            config=multitasking_config,
        )

        violations = policy.evaluate(context)
        rule_ids = [v.rule_id for v in violations]

        assert "BR-ASSIGN-004" not in rule_ids


class TestTaskSelectionPolicyWorkloadCapacity:
    """Tests for BR-ASSIGN-003: Workload capacity."""

    def test_cannot_select_if_workload_would_be_impossible(
        self,
        policy,
        default_config,
        project,
        employee_member,
    ):
        """Cannot select task if it would push workload to Impossible."""
        # Create tasks that bring workload close to limit
        # MID seniority = 1.0x multiplier, base capacity = 10
        # Effective capacity = 10, max ratio = 1.5, max score = 15
        heavy_task = Task(
            project_id=project.id,
            title="Heavy Task",
            difficulty_points=14,
        )
        heavy_task.select(employee_member.id)

        new_task = Task(
            project_id=project.id,
            title="New Task",
            difficulty_points=5,  # Would bring total to 19, ratio = 1.9 > 1.5
        )

        context = SelectionContext(
            task=new_task,
            project=project,
            member=employee_member,
            assigned_tasks=[heavy_task],
            dependencies=[],
            all_project_tasks=[heavy_task, new_task],
            config=default_config,
        )

        violations = policy.evaluate(context)
        rule_ids = [v.rule_id for v in violations]

        # Note: Also fails BR-ASSIGN-004 (single-task focus) with default config
        assert "BR-ASSIGN-003" in rule_ids

    def test_can_select_within_workload_limit(
        self,
        policy,
        project,
        employee_member,
    ):
        """Can select task if within workload capacity."""
        config = ProjectConfig(allow_multitasking=True)  # Disable single-task check

        light_task = Task(
            project_id=project.id,
            title="Light Task",
            difficulty_points=3,
        )
        light_task.select(employee_member.id)

        new_task = Task(
            project_id=project.id,
            title="New Task",
            difficulty_points=5,  # Total = 8, ratio = 0.8 < 1.5
        )

        context = SelectionContext(
            task=new_task,
            project=project,
            member=employee_member,
            assigned_tasks=[light_task],
            dependencies=[],
            all_project_tasks=[light_task, new_task],
            config=config,
        )

        violations = policy.evaluate(context)
        rule_ids = [v.rule_id for v in violations]

        assert "BR-ASSIGN-003" not in rule_ids


class TestTaskSelectionPolicyRoleMatch:
    """Tests for BR-ASSIGN-002: Role must match."""

    def test_cannot_select_task_with_different_role(
        self,
        policy,
        default_config,
        project,
        employee_member,
    ):
        """Cannot select task requiring different role."""
        different_role_id = uuid4()
        task = Task(
            project_id=project.id,
            title="Different Role Task",
            difficulty_points=5,
            required_role_id=different_role_id,
        )

        context = SelectionContext(
            task=task,
            project=project,
            member=employee_member,
            assigned_tasks=[],
            dependencies=[],
            all_project_tasks=[task],
            config=default_config,
        )

        violations = policy.evaluate(context)
        rule_ids = [v.rule_id for v in violations]

        assert "BR-ASSIGN-002" in rule_ids

    def test_can_select_task_with_matching_role(
        self,
        policy,
        default_config,
        project,
        employee_member,
        role_id,
    ):
        """Can select task with matching role."""
        task = Task(
            project_id=project.id,
            title="Matching Role Task",
            difficulty_points=5,
            required_role_id=role_id,
        )

        context = SelectionContext(
            task=task,
            project=project,
            member=employee_member,
            assigned_tasks=[],
            dependencies=[],
            all_project_tasks=[task],
            config=default_config,
        )

        violations = policy.evaluate(context)
        rule_ids = [v.rule_id for v in violations]

        assert "BR-ASSIGN-002" not in rule_ids

    def test_can_select_task_without_role_requirement(
        self,
        policy,
        default_config,
        project,
        employee_member,
    ):
        """Can select task without role requirement."""
        task = Task(
            project_id=project.id,
            title="No Role Required Task",
            difficulty_points=5,
            required_role_id=None,
        )

        context = SelectionContext(
            task=task,
            project=project,
            member=employee_member,
            assigned_tasks=[],
            dependencies=[],
            all_project_tasks=[task],
            config=default_config,
        )

        violations = policy.evaluate(context)
        rule_ids = [v.rule_id for v in violations]

        assert "BR-ASSIGN-002" not in rule_ids


class TestTaskSelectionPolicyHelperMethods:
    """Tests for policy helper methods."""

    def test_can_select_returns_true_when_no_violations(
        self,
        policy,
        default_config,
        project,
        employee_member,
        selectable_task,
    ):
        """can_select() returns True when task is selectable."""
        context = SelectionContext(
            task=selectable_task,
            project=project,
            member=employee_member,
            assigned_tasks=[],
            dependencies=[],
            all_project_tasks=[selectable_task],
            config=default_config,
        )

        assert policy.can_select(context) is True

    def test_can_select_returns_false_when_violations_exist(
        self,
        policy,
        default_config,
        project,
        manager_member,
        selectable_task,
    ):
        """can_select() returns False when violations exist."""
        context = SelectionContext(
            task=selectable_task,
            project=project,
            member=manager_member,
            assigned_tasks=[],
            dependencies=[],
            all_project_tasks=[selectable_task],
            config=default_config,
        )

        assert policy.can_select(context) is False

    def test_get_first_violation_returns_none_when_valid(
        self,
        policy,
        default_config,
        project,
        employee_member,
        selectable_task,
    ):
        """get_first_violation() returns None when task is selectable."""
        context = SelectionContext(
            task=selectable_task,
            project=project,
            member=employee_member,
            assigned_tasks=[],
            dependencies=[],
            all_project_tasks=[selectable_task],
            config=default_config,
        )

        assert policy.get_first_violation(context) is None

    def test_get_first_violation_returns_violation_when_invalid(
        self,
        policy,
        default_config,
        project,
        manager_member,
        selectable_task,
    ):
        """get_first_violation() returns first violation when invalid."""
        context = SelectionContext(
            task=selectable_task,
            project=project,
            member=manager_member,
            assigned_tasks=[],
            dependencies=[],
            all_project_tasks=[selectable_task],
            config=default_config,
        )

        violation = policy.get_first_violation(context)

        assert violation is not None
        assert violation.rule_id == "BR-PROJ-002"
