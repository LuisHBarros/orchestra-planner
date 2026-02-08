"""SQLAlchemy Unit of Work implementation."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyUnitOfWork:
    """
    Concrete Unit of Work backed by a SQLAlchemy AsyncSession.

    Manages a single database transaction: opens a session on enter,
    commits explicitly via commit(), and rolls back on unhandled exceptions.
    Repositories are instantiated inside __aenter__ so they share the
    same transactional session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        await self._session.begin()

        # Deferred imports to avoid circular dependencies and because
        # adapter implementations may not exist yet during early development.
        from backend.src.adapters.db import (
            PostgresProjectInviteRepository,
            PostgresProjectMemberRepository,
            PostgresProjectRepository,
            PostgresRoleRepository,
            PostgresCalendarRepository,
            PostgresTaskDependencyRepository,
            PostgresTaskLogRepository,
            PostgresTaskRepository,
            PostgresUserRepository,
        )

        self.user_repository = PostgresUserRepository(self._session)
        self.project_repository = PostgresProjectRepository(self._session)
        self.calendar_repository = PostgresCalendarRepository(self._session)
        self.project_member_repository = PostgresProjectMemberRepository(self._session)
        self.project_invite_repository = PostgresProjectInviteRepository(self._session)
        self.role_repository = PostgresRoleRepository(self._session)
        self.task_repository = PostgresTaskRepository(self._session)
        self.task_dependency_repository = PostgresTaskDependencyRepository(
            self._session
        )
        self.task_log_repository = PostgresTaskLogRepository(self._session)

        return self

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Roll back the current transaction."""
        await self._session.rollback()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
