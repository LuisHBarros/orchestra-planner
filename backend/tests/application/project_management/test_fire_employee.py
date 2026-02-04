"""Tests for FireEmployeeUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.project_management import (
    FireEmployeeInput,
    FireEmployeeUseCase,
    MemberNotFoundError,
)
from backend.src.domain.entities import (
    Project,
    ProjectMember,
    SeniorityLevel,
    Task,
    TaskStatus,
)
from backend.src.domain.errors import ManagerRequiredError, ProjectNotFoundError


@pytest.fixture
def project_repository():
    return AsyncMock()


@pytest.fixture
def project_member_repository():
    return AsyncMock()


@pytest.fixture
def task_repository():
    return AsyncMock()


@pytest.fixture
def use_case(project_repository, project_member_repository, task_repository):
    return FireEmployeeUseCase(
        project_repository=project_repository,
        project_member_repository=project_member_repository,
        task_repository=task_repository,
    )


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
def doing_task(project, employee_member):
    task = Task(
        project_id=project.id,
        title="In progress task",
        difficulty_points=5,
    )
    task.select(employee_member.id)
    return task


@pytest.fixture
def todo_task(project):
    return Task(
        project_id=project.id,
        title="Todo task",
        difficulty_points=3,
    )


class TestFireEmployeeUseCase:
    """Tests for FireEmployeeUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_fires_employee_successfully(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        project,
        employee_member,
        manager_user_id,
        employee_user_id,
    ):
        """Manager can fire an employee from the project."""
        project_repository.find_by_id.return_value = project
        project_member_repository.find_by_project_and_user.return_value = (
            employee_member
        )
        task_repository.find_by_project.return_value = []
        project_member_repository.delete.return_value = None

        input_data = FireEmployeeInput(
            project_id=project.id,
            employee_user_id=employee_user_id,
            manager_user_id=manager_user_id,
        )

        result = await use_case.execute(input_data)

        assert result == []
        project_member_repository.delete.assert_called_once_with(employee_member.id)

    @pytest.mark.asyncio
    async def test_unassigns_doing_tasks_when_firing(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        project,
        employee_member,
        doing_task,
        manager_user_id,
        employee_user_id,
    ):
        """Firing an employee unassigns all their Doing tasks."""
        project_repository.find_by_id.return_value = project
        project_member_repository.find_by_project_and_user.return_value = (
            employee_member
        )
        task_repository.find_by_project.return_value = [doing_task]
        task_repository.save_many.return_value = None
        project_member_repository.delete.return_value = None

        input_data = FireEmployeeInput(
            project_id=project.id,
            employee_user_id=employee_user_id,
            manager_user_id=manager_user_id,
        )

        result = await use_case.execute(input_data)

        assert len(result) == 1
        assert result[0].status == TaskStatus.TODO
        assert result[0].assignee_id is None
        task_repository.save_many.assert_called_once()

    @pytest.mark.asyncio
    async def test_does_not_affect_todo_tasks(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        project,
        employee_member,
        todo_task,
        manager_user_id,
        employee_user_id,
    ):
        """Firing an employee does not affect Todo tasks."""
        project_repository.find_by_id.return_value = project
        project_member_repository.find_by_project_and_user.return_value = (
            employee_member
        )
        task_repository.find_by_project.return_value = [todo_task]
        project_member_repository.delete.return_value = None

        input_data = FireEmployeeInput(
            project_id=project.id,
            employee_user_id=employee_user_id,
            manager_user_id=manager_user_id,
        )

        result = await use_case.execute(input_data)

        assert result == []
        task_repository.save_many.assert_not_called()

    @pytest.mark.asyncio
    async def test_handles_multiple_doing_tasks(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        project,
        employee_member,
        manager_user_id,
        employee_user_id,
    ):
        """Firing an employee unassigns all their Doing tasks."""
        task1 = Task(project_id=project.id, title="Task 1", difficulty_points=3)
        task1.select(employee_member.id)
        task2 = Task(project_id=project.id, title="Task 2", difficulty_points=5)
        task2.select(employee_member.id)

        project_repository.find_by_id.return_value = project
        project_member_repository.find_by_project_and_user.return_value = (
            employee_member
        )
        task_repository.find_by_project.return_value = [task1, task2]
        task_repository.save_many.return_value = None
        project_member_repository.delete.return_value = None

        input_data = FireEmployeeInput(
            project_id=project.id,
            employee_user_id=employee_user_id,
            manager_user_id=manager_user_id,
        )

        result = await use_case.execute(input_data)

        assert len(result) == 2
        assert all(task.status == TaskStatus.TODO for task in result)
        assert all(task.assignee_id is None for task in result)

    @pytest.mark.asyncio
    async def test_raises_project_not_found(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        manager_user_id,
        employee_user_id,
    ):
        """Should raise ProjectNotFoundError when project doesn't exist."""
        project_repository.find_by_id.return_value = None

        input_data = FireEmployeeInput(
            project_id=uuid4(),
            employee_user_id=employee_user_id,
            manager_user_id=manager_user_id,
        )

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_manager_required_when_not_manager(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        project,
        employee_user_id,
    ):
        """Should raise ManagerRequiredError when user is not the manager."""
        project_repository.find_by_id.return_value = project
        non_manager_id = uuid4()

        input_data = FireEmployeeInput(
            project_id=project.id,
            employee_user_id=employee_user_id,
            manager_user_id=non_manager_id,
        )

        with pytest.raises(ManagerRequiredError, match="fire employee"):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_member_not_found_when_not_member(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        project,
        manager_user_id,
    ):
        """Should raise MemberNotFoundError when employee is not a member."""
        project_repository.find_by_id.return_value = project
        project_member_repository.find_by_project_and_user.return_value = None
        non_member_user_id = uuid4()

        input_data = FireEmployeeInput(
            project_id=project.id,
            employee_user_id=non_member_user_id,
            manager_user_id=manager_user_id,
        )

        with pytest.raises(MemberNotFoundError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_value_error_when_firing_manager(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        project,
        manager_user_id,
        role_id,
    ):
        """Should raise ValueError when trying to fire the project manager."""
        manager_member = ProjectMember(
            project_id=project.id,
            user_id=manager_user_id,
            role_id=role_id,
            seniority_level=SeniorityLevel.LEAD,
        )
        project_repository.find_by_id.return_value = project
        project_member_repository.find_by_project_and_user.return_value = manager_member

        input_data = FireEmployeeInput(
            project_id=project.id,
            employee_user_id=manager_user_id,
            manager_user_id=manager_user_id,
        )

        with pytest.raises(ValueError, match="Cannot fire the project manager"):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_does_not_affect_other_members_tasks(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        project,
        employee_member,
        manager_user_id,
        employee_user_id,
        role_id,
    ):
        """Firing one employee does not affect another employee's tasks."""
        other_member = ProjectMember(
            project_id=project.id,
            user_id=uuid4(),
            role_id=role_id,
            seniority_level=SeniorityLevel.SENIOR,
        )
        other_task = Task(
            project_id=project.id, title="Other task", difficulty_points=5
        )
        other_task.select(other_member.id)

        project_repository.find_by_id.return_value = project
        project_member_repository.find_by_project_and_user.return_value = (
            employee_member
        )
        task_repository.find_by_project.return_value = [other_task]
        project_member_repository.delete.return_value = None

        input_data = FireEmployeeInput(
            project_id=project.id,
            employee_user_id=employee_user_id,
            manager_user_id=manager_user_id,
        )

        result = await use_case.execute(input_data)

        assert result == []
        assert other_task.status == TaskStatus.DOING
        assert other_task.assignee_id == other_member.id
