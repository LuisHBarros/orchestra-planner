"""Tests for ResignFromProjectUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.project_management import (
    ManagerCannotResignError,
    ResignFromProjectInput,
    ResignFromProjectUseCase,
)
from backend.src.application.use_cases.project_management.resign_from_project import (
    MemberNotFoundError,
)
from backend.src.domain.entities import (
    Project,
    ProjectMember,
    SeniorityLevel,
    Task,
    TaskStatus,
)
from backend.src.domain.errors import ProjectNotFoundError


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
    return ResignFromProjectUseCase(
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


class TestResignFromProjectUseCase:
    """Tests for ResignFromProjectUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_resigns_successfully(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        project,
        employee_member,
        employee_user_id,
    ):
        """Employee can resign from the project."""
        project_repository.find_by_id.return_value = project
        project_member_repository.find_by_project_and_user.return_value = (
            employee_member
        )
        task_repository.find_by_project.return_value = []
        project_member_repository.delete.return_value = None

        input_data = ResignFromProjectInput(
            project_id=project.id,
            user_id=employee_user_id,
        )

        result = await use_case.execute(input_data)

        assert result == []
        project_member_repository.delete.assert_called_once_with(employee_member.id)

    @pytest.mark.asyncio
    async def test_unassigns_doing_tasks_when_resigning(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        project,
        employee_member,
        doing_task,
        employee_user_id,
    ):
        """Resigning unassigns all employee's Doing tasks."""
        project_repository.find_by_id.return_value = project
        project_member_repository.find_by_project_and_user.return_value = (
            employee_member
        )
        task_repository.find_by_project.return_value = [doing_task]
        task_repository.save_many.return_value = None
        project_member_repository.delete.return_value = None

        input_data = ResignFromProjectInput(
            project_id=project.id,
            user_id=employee_user_id,
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
        employee_user_id,
    ):
        """Resigning does not affect Todo tasks."""
        project_repository.find_by_id.return_value = project
        project_member_repository.find_by_project_and_user.return_value = (
            employee_member
        )
        task_repository.find_by_project.return_value = [todo_task]
        project_member_repository.delete.return_value = None

        input_data = ResignFromProjectInput(
            project_id=project.id,
            user_id=employee_user_id,
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
        employee_user_id,
    ):
        """Resigning unassigns all employee's Doing tasks."""
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

        input_data = ResignFromProjectInput(
            project_id=project.id,
            user_id=employee_user_id,
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
        employee_user_id,
    ):
        """Should raise ProjectNotFoundError when project doesn't exist."""
        project_repository.find_by_id.return_value = None

        input_data = ResignFromProjectInput(
            project_id=uuid4(),
            user_id=employee_user_id,
        )

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_manager_cannot_resign(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        project,
        manager_user_id,
    ):
        """Should raise ManagerCannotResignError when manager tries to resign."""
        project_repository.find_by_id.return_value = project

        input_data = ResignFromProjectInput(
            project_id=project.id,
            user_id=manager_user_id,
        )

        with pytest.raises(ManagerCannotResignError):
            await use_case.execute(input_data)

        # Should not proceed to member lookup
        project_member_repository.find_by_project_and_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_member_not_found_when_not_member(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        project,
    ):
        """Should raise MemberNotFoundError when user is not a member."""
        project_repository.find_by_id.return_value = project
        project_member_repository.find_by_project_and_user.return_value = None
        non_member_user_id = uuid4()

        input_data = ResignFromProjectInput(
            project_id=project.id,
            user_id=non_member_user_id,
        )

        with pytest.raises(MemberNotFoundError):
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
        employee_user_id,
        role_id,
    ):
        """Resigning does not affect another employee's tasks."""
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

        input_data = ResignFromProjectInput(
            project_id=project.id,
            user_id=employee_user_id,
        )

        result = await use_case.execute(input_data)

        assert result == []
        assert other_task.status == TaskStatus.DOING
        assert other_task.assignee_id == other_member.id

    @pytest.mark.asyncio
    async def test_tasks_can_be_selected_after_resignation(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        project,
        employee_member,
        doing_task,
        employee_user_id,
        role_id,
    ):
        """Tasks unassigned due to resignation can be selected by others."""
        project_repository.find_by_id.return_value = project
        project_member_repository.find_by_project_and_user.return_value = (
            employee_member
        )
        task_repository.find_by_project.return_value = [doing_task]
        task_repository.save_many.return_value = None
        project_member_repository.delete.return_value = None

        input_data = ResignFromProjectInput(
            project_id=project.id,
            user_id=employee_user_id,
        )

        result = await use_case.execute(input_data)

        # Task should be selectable again
        assert result[0].can_be_selected() is True

        # Another member can select it
        new_member = ProjectMember(
            project_id=project.id,
            user_id=uuid4(),
            role_id=role_id,
            seniority_level=SeniorityLevel.MID,
        )
        result[0].select(new_member.id)
        assert result[0].status == TaskStatus.DOING
        assert result[0].assignee_id == new_member.id
