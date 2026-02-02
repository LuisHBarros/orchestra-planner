"""Domain layer for Orchestra Planner.

This package contains pure business logic with zero external dependencies.

Structure:
- entities/: Core domain entities (User, Task, Project, etc.)
- errors/: Domain-specific exceptions (AuthError, TaskError, etc.)
- ports/: Interface definitions for external systems (repositories, services)
- rules/: Business rule constants (BR-TASK-*, BR-AUTH-*, etc.)
"""

import backend.src.domain.errors as errors
import backend.src.domain.ports as ports
import backend.src.domain.ports.repositories as repositories
from backend.src.domain.entities import (
    InviteStatus,
    Project,
    ProjectInvite,
    ProjectMember,
    Role,
    SeniorityLevel,
    Task,
    TaskDependency,
    TaskLog,
    TaskLogType,
    TaskStatus,
    User,
    Workload,
    WorkloadStatus,
)
