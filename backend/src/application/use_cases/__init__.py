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
    CompleteTaskInput,
    CompleteTaskUseCase,
    CreateTaskInput,
    CreateTaskUseCase,
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
    "CompleteTaskInput",
    "CompleteTaskUseCase",
    "CreateTaskInput",
    "CreateTaskUseCase",
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
