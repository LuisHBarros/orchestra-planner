"""Project management use cases."""

from backend.src.application.use_cases.project_management.configure_project_llm import (
    ConfigureProjectLLMInput,
    ConfigureProjectLLMUseCase,
)
from backend.src.application.use_cases.project_management.configure_calendar import (
    ConfigureCalendarInput,
    ConfigureCalendarUseCase,
)
from backend.src.application.use_cases.project_management.create_project import (
    CreateProjectInput,
    CreateProjectUseCase,
)
from backend.src.application.use_cases.project_management.create_role import (
    CreateRoleInput,
    CreateRoleUseCase,
)
from backend.src.application.use_cases.project_management.fire_employee import (
    FireEmployeeInput,
    FireEmployeeUseCase,
    MemberNotFoundError,
)
from backend.src.application.use_cases.project_management.get_project_details import (
    GetProjectDetailsInput,
    GetProjectDetailsOutput,
    GetProjectDetailsUseCase,
)
from backend.src.application.use_cases.project_management.list_project_members import (
    EnrichedMember,
    ListProjectMembersInput,
    ListProjectMembersOutput,
    ListProjectMembersUseCase,
)
from backend.src.application.use_cases.project_management.list_user_projects import (
    ListUserProjectsInput,
    ListUserProjectsOutput,
    ListUserProjectsUseCase,
)
from backend.src.application.use_cases.project_management.recalculate_project_schedule import (
    RecalculateProjectScheduleInput,
    RecalculateProjectScheduleUseCase,
)
from backend.src.application.use_cases.project_management.resign_from_project import (
    ManagerCannotResignError,
    ResignFromProjectInput,
    ResignFromProjectUseCase,
)

__all__ = [
    "ConfigureProjectLLMInput",
    "ConfigureProjectLLMUseCase",
    "ConfigureCalendarInput",
    "ConfigureCalendarUseCase",
    "CreateProjectInput",
    "CreateProjectUseCase",
    "CreateRoleInput",
    "CreateRoleUseCase",
    "EnrichedMember",
    "FireEmployeeInput",
    "FireEmployeeUseCase",
    "GetProjectDetailsInput",
    "GetProjectDetailsOutput",
    "GetProjectDetailsUseCase",
    "ListProjectMembersInput",
    "ListProjectMembersOutput",
    "ListProjectMembersUseCase",
    "ListUserProjectsInput",
    "ListUserProjectsOutput",
    "ListUserProjectsUseCase",
    "ManagerCannotResignError",
    "MemberNotFoundError",
    "RecalculateProjectScheduleInput",
    "RecalculateProjectScheduleUseCase",
    "ResignFromProjectInput",
    "ResignFromProjectUseCase",
]
