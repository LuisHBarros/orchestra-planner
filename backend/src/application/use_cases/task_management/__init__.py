"""Task management use cases."""

from backend.src.application.use_cases.task_management.abandon_task import (
    AbandonTaskInput,
    AbandonTaskUseCase,
)
from backend.src.application.use_cases.task_management.add_task_report import (
    AddTaskReportInput,
    AddTaskReportUseCase,
)
from backend.src.application.use_cases.task_management.complete_task import (
    CompleteTaskInput,
    CompleteTaskUseCase,
)
from backend.src.application.use_cases.task_management.add_dependency import (
    AddDependencyInput,
    AddDependencyUseCase,
)
from backend.src.application.use_cases.task_management.cancel_task import (
    CancelTaskInput,
    CancelTaskUseCase,
)
from backend.src.application.use_cases.task_management.create_task import (
    CreateTaskInput,
    CreateTaskUseCase,
)
from backend.src.application.use_cases.task_management.delete_task import (
    DeleteTaskInput,
    DeleteTaskUseCase,
)
from backend.src.application.use_cases.task_management.remove_from_task import (
    RemoveFromTaskInput,
    RemoveFromTaskUseCase,
)
from backend.src.application.use_cases.task_management.remove_dependency import (
    RemoveDependencyInput,
    RemoveDependencyUseCase,
)
from backend.src.application.use_cases.task_management.select_task import (
    SelectTaskInput,
    SelectTaskUseCase,
)

__all__ = [
    "AbandonTaskInput",
    "AbandonTaskUseCase",
    "AddTaskReportInput",
    "AddTaskReportUseCase",
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
    "RemoveFromTaskInput",
    "RemoveFromTaskUseCase",
    "RemoveDependencyInput",
    "RemoveDependencyUseCase",
    "SelectTaskInput",
    "SelectTaskUseCase",
]
