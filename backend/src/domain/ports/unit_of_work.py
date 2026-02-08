"""Unit of Work port for transactional consistency."""

from __future__ import annotations

from typing import Protocol

from backend.src.domain.ports.repositories import (
    CalendarRepository,
    ProjectInviteRepository,
    ProjectMemberRepository,
    ProjectRepository,
    RoleRepository,
    TaskDependencyRepository,
    TaskLogRepository,
    TaskRepository,
    UserRepository,
)


class UnitOfWork(Protocol):
    """
    Port for managing transactional boundaries across multiple repositories.

    Ensures all-or-nothing semantics for use cases that modify multiple
    entities (e.g., FireEmployee: save_many tasks + delete member).

    Usage:
        async with uow:
            await uow.task_repository.save_many(tasks)
            await uow.project_member_repository.delete(member_id)
            await uow.commit()
        # If any operation raises, __aexit__ triggers rollback.
    """

    user_repository: UserRepository
    project_repository: ProjectRepository
    calendar_repository: CalendarRepository
    project_member_repository: ProjectMemberRepository
    project_invite_repository: ProjectInviteRepository
    role_repository: RoleRepository
    task_repository: TaskRepository
    task_dependency_repository: TaskDependencyRepository
    task_log_repository: TaskLogRepository

    async def __aenter__(self) -> UnitOfWork: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
