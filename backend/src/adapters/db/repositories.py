"""PostgreSQL repository implementations using SQLAlchemy AsyncSession."""

from __future__ import annotations

from typing import Iterable
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.domain.entities import Calendar, Task, TaskDependency, TaskLog
from backend.src.domain.entities import Project, ProjectInvite, ProjectMember, Role, User
from backend.src.domain.entities.working_calendar import WorkingCalendar
from backend.src.infrastructure.db.models import (
    CalendarModel,
    ProjectInviteModel,
    ProjectMemberModel,
    ProjectModel,
    RoleModel,
    TaskDependencyModel,
    TaskLogModel,
    TaskModel,
    UserModel,
)


class PostgresProjectRepository:
    """SQLAlchemy repository for Project entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, project_id: UUID) -> Project | None:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        project = model.to_entity()

        calendar_result = await self._session.execute(
            select(CalendarModel).where(CalendarModel.project_id == project_id)
        )
        calendar_model = calendar_result.scalar_one_or_none()
        if calendar_model:
            calendar = calendar_model.to_entity()
            project.calendar = WorkingCalendar.from_calendar(calendar)
        return project

    async def save(self, project: Project) -> Project:
        model = ProjectModel.from_entity(project)
        await self._session.merge(model)
        await self._session.flush()
        return project

    async def delete(self, project_id: UUID) -> None:
        await self._session.execute(
            delete(ProjectModel).where(ProjectModel.id == project_id)
        )


class PostgresCalendarRepository:
    """SQLAlchemy repository for Calendar entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_project_id(self, project_id: UUID) -> Calendar | None:
        result = await self._session.execute(
            select(CalendarModel).where(CalendarModel.project_id == project_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def save(self, calendar: Calendar) -> Calendar:
        model = CalendarModel.from_entity(calendar)
        await self._session.merge(model)
        await self._session.flush()
        return calendar


class PostgresProjectMemberRepository:
    """SQLAlchemy repository for ProjectMember entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, project_member_id: UUID) -> ProjectMember | None:
        result = await self._session.execute(
            select(ProjectMemberModel).where(ProjectMemberModel.id == project_member_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def find_by_project(self, project_id: UUID) -> list[ProjectMember]:
        result = await self._session.execute(
            select(ProjectMemberModel).where(ProjectMemberModel.project_id == project_id)
        )
        return [m.to_entity() for m in result.scalars().all()]

    async def find_by_project_and_user(
        self, project_id: UUID, user_id: UUID
    ) -> ProjectMember | None:
        result = await self._session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def save(self, project_member: ProjectMember) -> ProjectMember:
        model = ProjectMemberModel.from_entity(project_member)
        await self._session.merge(model)
        await self._session.flush()
        return project_member

    async def delete(self, project_member_id: UUID) -> None:
        await self._session.execute(
            delete(ProjectMemberModel).where(ProjectMemberModel.id == project_member_id)
        )


class PostgresProjectInviteRepository:
    """SQLAlchemy repository for ProjectInvite entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_token(self, token: str) -> ProjectInvite | None:
        result = await self._session.execute(
            select(ProjectInviteModel).where(ProjectInviteModel.token == token)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def find_by_project(self, project_id: UUID) -> list[ProjectInvite]:
        result = await self._session.execute(
            select(ProjectInviteModel).where(ProjectInviteModel.project_id == project_id)
        )
        return [m.to_entity() for m in result.scalars().all()]

    async def save(self, project_invite: ProjectInvite) -> ProjectInvite:
        model = ProjectInviteModel.from_entity(project_invite)
        await self._session.merge(model)
        await self._session.flush()
        return project_invite

    async def delete(self, token: str) -> None:
        await self._session.execute(
            delete(ProjectInviteModel).where(ProjectInviteModel.token == token)
        )


class PostgresRoleRepository:
    """SQLAlchemy repository for Role entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, role_id: UUID) -> Role | None:
        result = await self._session.execute(
            select(RoleModel).where(RoleModel.id == role_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def save(self, role: Role) -> Role:
        model = RoleModel.from_entity(role)
        await self._session.merge(model)
        await self._session.flush()
        return role

    async def delete(self, role_id: UUID) -> None:
        await self._session.execute(delete(RoleModel).where(RoleModel.id == role_id))


class PostgresTaskRepository:
    """SQLAlchemy repository for Task entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, task_id: UUID) -> Task | None:
        result = await self._session.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def find_by_project(self, project_id: UUID) -> list[Task]:
        result = await self._session.execute(
            select(TaskModel).where(TaskModel.project_id == project_id)
        )
        return [m.to_entity() for m in result.scalars().all()]

    async def find_by_assignee(self, assignee_id: UUID) -> list[Task]:
        result = await self._session.execute(
            select(TaskModel).where(TaskModel.assignee_id == assignee_id)
        )
        return [m.to_entity() for m in result.scalars().all()]

    async def save(self, task: Task) -> Task:
        model = TaskModel.from_entity(task)
        await self._session.merge(model)
        await self._session.flush()
        return task

    async def save_many(self, tasks: list[Task]) -> list[Task]:
        await self._merge_many(TaskModel, (TaskModel.from_entity(t) for t in tasks))
        return tasks

    async def delete(self, task_id: UUID) -> None:
        await self._session.execute(delete(TaskModel).where(TaskModel.id == task_id))

    async def _merge_many(self, model_type, models: Iterable) -> None:
        for model in models:
            await self._session.merge(model)
        await self._session.flush()


class PostgresTaskDependencyRepository:
    """SQLAlchemy repository for TaskDependency entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, task_dependency: TaskDependency) -> TaskDependency:
        model = TaskDependencyModel.from_entity(task_dependency)
        await self._session.merge(model)
        await self._session.flush()
        return task_dependency

    async def find_by_id(self, dependency_id: UUID) -> TaskDependency | None:
        result = await self._session.execute(
            select(TaskDependencyModel).where(
                (TaskDependencyModel.blocking_task_id == dependency_id)
                | (TaskDependencyModel.blocked_task_id == dependency_id)
            )
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def find_by_project(self, project_id: UUID) -> list[TaskDependency]:
        result = await self._session.execute(
            select(TaskDependencyModel)
            .join(TaskModel, TaskDependencyModel.blocking_task_id == TaskModel.id)
            .where(TaskModel.project_id == project_id)
        )
        return [m.to_entity() for m in result.scalars().all()]

    async def find_by_tasks(
        self, blocking_task_id: UUID, blocked_task_id: UUID
    ) -> TaskDependency | None:
        result = await self._session.execute(
            select(TaskDependencyModel).where(
                TaskDependencyModel.blocking_task_id == blocking_task_id,
                TaskDependencyModel.blocked_task_id == blocked_task_id,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def delete(self, dependency_id: UUID) -> None:
        await self._session.execute(
            delete(TaskDependencyModel).where(
                (TaskDependencyModel.blocking_task_id == dependency_id)
                | (TaskDependencyModel.blocked_task_id == dependency_id)
            )
        )

    async def delete_by_tasks(self, blocking_task_id: UUID, blocked_task_id: UUID) -> None:
        await self._session.execute(
            delete(TaskDependencyModel).where(
                TaskDependencyModel.blocking_task_id == blocking_task_id,
                TaskDependencyModel.blocked_task_id == blocked_task_id,
            )
        )


class PostgresTaskLogRepository:
    """SQLAlchemy repository for TaskLog entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, task_log: TaskLog) -> TaskLog:
        model = TaskLogModel.from_entity(task_log)
        await self._session.merge(model)
        await self._session.flush()
        return task_log

    async def find_by_task(self, task_id: UUID) -> list[TaskLog]:
        result = await self._session.execute(
            select(TaskLogModel).where(TaskLogModel.task_id == task_id)
        )
        return [m.to_entity() for m in result.scalars().all()]

    async def find_by_author(self, author_id: UUID) -> list[TaskLog]:
        result = await self._session.execute(
            select(TaskLogModel).where(TaskLogModel.author_id == author_id)
        )
        return [m.to_entity() for m in result.scalars().all()]


class PostgresUserRepository:
    """SQLAlchemy repository for User entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> User:
        model = UserModel.from_entity(user)
        await self._session.merge(model)
        await self._session.flush()
        return user

    async def find_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def find_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email.strip().lower())
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def find_by_magic_link_token_hash(self, token_hash: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.magic_link_token_hash == token_hash)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def update(self, user: User) -> User:
        return await self.save(user)

    async def delete(self, user_id: UUID) -> None:
        await self._session.execute(delete(UserModel).where(UserModel.id == user_id))
