"""Application use cases."""

from backend.src.application.use_cases.auth import (
    RequestMagicLinkUseCase,
    VerifyMagicLinkUseCase,
)
from backend.src.application.use_cases.invitations import (
    AcceptInviteInput,
    AcceptInviteOutput,
    AcceptInviteUseCase,
    CreateInviteInput,
    CreateInviteOutput,
    CreateInviteUseCase,
)
from backend.src.application.use_cases.project_management import (
    ConfigureCalendarInput,
    ConfigureCalendarUseCase,
    ConfigureProjectLLMInput,
    ConfigureProjectLLMUseCase,
    CreateProjectInput,
    CreateProjectUseCase,
    CreateRoleInput,
    CreateRoleUseCase,
    GetProjectDetailsInput,
    GetProjectDetailsOutput,
    GetProjectDetailsUseCase,
)
from backend.src.application.use_cases.task_management import (
    AbandonTaskInput,
    AbandonTaskUseCase,
    AddDependencyInput,
    AddDependencyUseCase,
    CompleteTaskInput,
    CompleteTaskUseCase,
    CancelTaskInput,
    CancelTaskUseCase,
    CreateTaskInput,
    CreateTaskUseCase,
    DeleteTaskInput,
    DeleteTaskUseCase,
    RemoveDependencyInput,
    RemoveDependencyUseCase,
    SelectTaskInput,
    SelectTaskUseCase,
)

__all__ = [
    # Auth
    "RequestMagicLinkUseCase",
    "VerifyMagicLinkUseCase",
    # Project Management
    "ConfigureProjectLLMInput",
    "ConfigureProjectLLMUseCase",
    "ConfigureCalendarInput",
    "ConfigureCalendarUseCase",
    "CreateProjectInput",
    "CreateProjectUseCase",
    "CreateRoleInput",
    "CreateRoleUseCase",
    "GetProjectDetailsInput",
    "GetProjectDetailsOutput",
    "GetProjectDetailsUseCase",
    # Task Management
    "AbandonTaskInput",
    "AbandonTaskUseCase",
    "AddDependencyInput",
    "AddDependencyUseCase",
    "CompleteTaskInput",
    "CompleteTaskUseCase",
    "CancelTaskInput",
    "CancelTaskUseCase",
    "CreateTaskInput",
    "CreateTaskUseCase",
    "DeleteTaskInput",
    "DeleteTaskUseCase",
    "RemoveDependencyInput",
    "RemoveDependencyUseCase",
    "SelectTaskInput",
    "SelectTaskUseCase",
    # Invitations
    "AcceptInviteInput",
    "AcceptInviteOutput",
    "AcceptInviteUseCase",
    "CreateInviteInput",
    "CreateInviteOutput",
    "CreateInviteUseCase",
]
