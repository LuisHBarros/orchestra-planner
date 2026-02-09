"""Dependency Injection container for the application."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.src.application.use_cases.auth import (
    RequestMagicLinkUseCase,
    VerifyMagicLinkUseCase,
)
from backend.src.application.use_cases.invitations import (
    AcceptInviteUseCase,
    CreateInviteUseCase,
)
from backend.src.application.use_cases.project_management import (
    ConfigureCalendarUseCase,
    ConfigureProjectLLMUseCase,
    CreateProjectUseCase,
    CreateRoleUseCase,
    FireEmployeeUseCase,
    GetProjectDetailsUseCase,
    ListProjectMembersUseCase,
    ListUserProjectsUseCase,
    RecalculateProjectScheduleUseCase,
    ResignFromProjectUseCase,
)
from backend.src.application.use_cases.task_management import (
    AbandonTaskUseCase,
    AddDependencyUseCase,
    AddTaskReportUseCase,
    CancelTaskUseCase,
    CompleteTaskUseCase,
    CreateTaskUseCase,
    DeleteTaskUseCase,
    RemoveDependencyUseCase,
    RemoveFromTaskUseCase,
    SelectTaskUseCase,
)
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
from backend.src.domain.ports.services import (
    EmailService,
    EncryptionService,
    LLMService,
    NotificationService,
    TokenService,
)
from backend.src.domain.ports.unit_of_work import UnitOfWork
from backend.src.domain.services.schedule_calculator import ScheduleCalculator
from backend.src.domain.services.task_selection_policy import TaskSelectionPolicy

if TYPE_CHECKING:
    from backend.src.domain.entities import ProjectConfig


@dataclass
class Repositories:
    """Container for all repository instances."""

    user: UserRepository
    project: ProjectRepository
    calendar: CalendarRepository
    project_member: ProjectMemberRepository
    project_invite: ProjectInviteRepository
    role: RoleRepository
    task: TaskRepository
    task_dependency: TaskDependencyRepository
    task_log: TaskLogRepository


@dataclass
class Services:
    """Container for all external service instances."""

    email: EmailService
    token: TokenService
    encryption: EncryptionService
    llm: LLMService | None = None
    notification: NotificationService | None = None


@dataclass
class DomainServices:
    """Container for domain service instances."""

    schedule_calculator: ScheduleCalculator = field(default_factory=ScheduleCalculator)
    task_selection_policy: TaskSelectionPolicy = field(
        default_factory=TaskSelectionPolicy
    )


@dataclass
class Container:
    """
    Dependency Injection container.

    Wires together repositories, services, and use cases.
    Each request gets its own Container instance with a fresh session.
    """

    repositories: Repositories
    services: Services
    uow: UnitOfWork
    public_base_url: str = "http://localhost:8000"
    domain_services: DomainServices = field(default_factory=DomainServices)
    config: "ProjectConfig | None" = None

    # --- Auth Use Cases ---

    def request_magic_link_use_case(self) -> RequestMagicLinkUseCase:
        """Create RequestMagicLinkUseCase with dependencies."""
        return RequestMagicLinkUseCase(
            uow=self.uow,
            email_service=self.services.email,
        )

    def verify_magic_link_use_case(self) -> VerifyMagicLinkUseCase:
        """Create VerifyMagicLinkUseCase with dependencies."""
        return VerifyMagicLinkUseCase(
            uow=self.uow,
            token_service=self.services.token,
        )

    # --- Project Management Use Cases ---

    def create_project_use_case(self) -> CreateProjectUseCase:
        """Create CreateProjectUseCase with dependencies."""
        return CreateProjectUseCase(uow=self.uow)

    def configure_project_llm_use_case(self) -> ConfigureProjectLLMUseCase:
        """Create ConfigureProjectLLMUseCase with dependencies."""
        return ConfigureProjectLLMUseCase(
            uow=self.uow,
            encryption_service=self.services.encryption,
        )

    def configure_calendar_use_case(self) -> ConfigureCalendarUseCase:
        """Create ConfigureCalendarUseCase with dependencies."""
        return ConfigureCalendarUseCase(
            uow=self.uow,
            recalculate_schedule_use_case=self.recalculate_project_schedule_use_case(),
        )

    def create_role_use_case(self) -> CreateRoleUseCase:
        """Create CreateRoleUseCase with dependencies."""
        return CreateRoleUseCase(uow=self.uow)

    def list_user_projects_use_case(self) -> ListUserProjectsUseCase:
        """Create ListUserProjectsUseCase with dependencies."""
        return ListUserProjectsUseCase(uow=self.uow)

    def list_project_members_use_case(self) -> ListProjectMembersUseCase:
        """Create ListProjectMembersUseCase with dependencies."""
        return ListProjectMembersUseCase(uow=self.uow)

    def get_project_details_use_case(self) -> GetProjectDetailsUseCase:
        """Create GetProjectDetailsUseCase with dependencies."""
        return GetProjectDetailsUseCase(uow=self.uow)

    def fire_employee_use_case(self) -> FireEmployeeUseCase:
        """Create FireEmployeeUseCase with dependencies."""
        return FireEmployeeUseCase(uow=self.uow)

    def resign_from_project_use_case(self) -> ResignFromProjectUseCase:
        """Create ResignFromProjectUseCase with dependencies."""
        return ResignFromProjectUseCase(uow=self.uow)

    def recalculate_project_schedule_use_case(
        self,
    ) -> RecalculateProjectScheduleUseCase:
        """Create RecalculateProjectScheduleUseCase with UoW."""
        return RecalculateProjectScheduleUseCase(
            uow=self.uow,
            schedule_calculator=self.domain_services.schedule_calculator,
        )

    # --- Invitation Use Cases ---

    def create_invite_use_case(self) -> CreateInviteUseCase:
        """Create CreateInviteUseCase with dependencies."""
        return CreateInviteUseCase(
            uow=self.uow,
            base_url=self.public_base_url,
        )

    def accept_invite_use_case(self) -> AcceptInviteUseCase:
        """Create AcceptInviteUseCase with dependencies."""
        return AcceptInviteUseCase(uow=self.uow)

    # --- Task Management Use Cases ---

    def create_task_use_case(self) -> CreateTaskUseCase:
        """Create CreateTaskUseCase with dependencies."""
        return CreateTaskUseCase(uow=self.uow)

    def cancel_task_use_case(self) -> CancelTaskUseCase:
        """Create CancelTaskUseCase with dependencies."""
        return CancelTaskUseCase(
            uow=self.uow,
            recalculate_schedule_use_case=self.recalculate_project_schedule_use_case(),
        )

    def delete_task_use_case(self) -> DeleteTaskUseCase:
        """Create DeleteTaskUseCase with dependencies."""
        return DeleteTaskUseCase(
            uow=self.uow,
            recalculate_schedule_use_case=self.recalculate_project_schedule_use_case(),
        )

    def add_dependency_use_case(self) -> AddDependencyUseCase:
        """Create AddDependencyUseCase with dependencies."""
        return AddDependencyUseCase(
            uow=self.uow,
            recalculate_schedule_use_case=self.recalculate_project_schedule_use_case(),
        )

    def remove_dependency_use_case(self) -> RemoveDependencyUseCase:
        """Create RemoveDependencyUseCase with dependencies."""
        return RemoveDependencyUseCase(
            uow=self.uow,
            recalculate_schedule_use_case=self.recalculate_project_schedule_use_case(),
        )

    def select_task_use_case(self) -> SelectTaskUseCase:
        """Create SelectTaskUseCase with dependencies."""
        return SelectTaskUseCase(
            uow=self.uow,
            selection_policy=self.domain_services.task_selection_policy,
            config=self.config,
        )

    def complete_task_use_case(self) -> CompleteTaskUseCase:
        """Create CompleteTaskUseCase with dependencies."""
        return CompleteTaskUseCase(uow=self.uow)

    def abandon_task_use_case(self) -> AbandonTaskUseCase:
        """Create AbandonTaskUseCase with dependencies."""
        return AbandonTaskUseCase(uow=self.uow)

    def add_task_report_use_case(self) -> AddTaskReportUseCase:
        """Create AddTaskReportUseCase with dependencies."""
        return AddTaskReportUseCase(uow=self.uow)

    def remove_from_task_use_case(self) -> RemoveFromTaskUseCase:
        """Create RemoveFromTaskUseCase with dependencies."""
        return RemoveFromTaskUseCase(uow=self.uow)


class ContainerFactory:
    """
    Factory for creating Container instances.

    Creates repository and service instances from a database session.
    This is where the actual adapter implementations are wired in.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        email_service: EmailService,
        token_service: TokenService,
        encryption_service: EncryptionService,
        llm_service: LLMService | None = None,
        notification_service: NotificationService | None = None,
        public_base_url: str = "http://localhost:8000",
    ):
        """
        Initialize the factory with service implementations.

        Services are typically singletons, while repositories are
        created per-request with the session. The session_factory is
        used to create Unit of Work instances with dedicated sessions.
        """
        self._session_factory = session_factory
        self._email_service = email_service
        self._token_service = token_service
        self._encryption_service = encryption_service
        self._llm_service = llm_service
        self._notification_service = notification_service
        self._public_base_url = public_base_url

    def get_email_service(self) -> EmailService:
        """Expose configured email service (used for local debugging)."""
        return self._email_service

    def create(
        self,
        session: AsyncSession,
        config: "ProjectConfig | None" = None,
    ) -> Container:
        """
        Create a Container with all dependencies wired.

        Args:
            session: The database session for this request.
            config: Optional project configuration overrides.

        Returns:
            A fully configured Container instance.
        """
        # Import adapters here to avoid circular imports
        # These will be implemented in backend/src/adapters/db/
        from backend.src.adapters.db import (
            PostgresCalendarRepository,
            PostgresProjectInviteRepository,
            PostgresProjectMemberRepository,
            PostgresProjectRepository,
            PostgresRoleRepository,
            PostgresTaskDependencyRepository,
            PostgresTaskLogRepository,
            PostgresTaskRepository,
            PostgresUserRepository,
        )

        from backend.src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork

        repositories = Repositories(
            user=PostgresUserRepository(session),
            project=PostgresProjectRepository(session),
            calendar=PostgresCalendarRepository(session),
            project_member=PostgresProjectMemberRepository(session),
            project_invite=PostgresProjectInviteRepository(session),
            role=PostgresRoleRepository(session),
            task=PostgresTaskRepository(session),
            task_dependency=PostgresTaskDependencyRepository(session),
            task_log=PostgresTaskLogRepository(session),
        )

        services = Services(
            email=self._email_service,
            token=self._token_service,
            encryption=self._encryption_service,
            llm=self._llm_service,
            notification=self._notification_service,
        )

        uow = SqlAlchemyUnitOfWork(session)

        return Container(
            repositories=repositories,
            services=services,
            uow=uow,
            public_base_url=self._public_base_url,
            config=config,
        )


async def get_container(
    session: AsyncSession,
    factory: ContainerFactory,
    config: "ProjectConfig | None" = None,
) -> Container:
    """
    FastAPI dependency for obtaining a Container.

    Usage in routes:
        @router.post("/projects")
        async def create_project(
            input: CreateProjectRequest,
            container: Container = Depends(get_container),
        ):
            use_case = container.create_project_use_case()
            return await use_case.execute(input)
    """
    return factory.create(session, config)
