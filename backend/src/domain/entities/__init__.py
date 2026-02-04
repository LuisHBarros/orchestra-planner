"""Domain entities for Orchestra Planner."""

from .project import Project
from .project_config import ProjectConfig, WorkloadThresholds
from .project_invite import INVITE_EXPIRATION_DAYS, InviteStatus, ProjectInvite
from .project_member import ProjectMember
from .role import Role
from .seniority_level import SeniorityLevel
from .task import VALID_STATUS_TRANSITIONS, Task, TaskStatus
from .task_dependency import TaskDependency, detect_circular_dependency
from .task_log import TaskLog, TaskLogType
from .user import MAGIC_LINK_EXPIRATION_MINUTES, User
from .workload import DEFAULT_BASE_CAPACITY, Workload, WorkloadStatus

__all__ = [
    # User & Auth
    "User",
    "MAGIC_LINK_EXPIRATION_MINUTES",
    # Project
    "Project",
    "ProjectConfig",
    "ProjectMember",
    "ProjectInvite",
    "InviteStatus",
    "INVITE_EXPIRATION_DAYS",
    # Roles & Seniority
    "Role",
    "SeniorityLevel",
    # Tasks
    "Task",
    "TaskStatus",
    "VALID_STATUS_TRANSITIONS",
    "TaskDependency",
    "detect_circular_dependency",
    "TaskLog",
    "TaskLogType",
    # Workload
    "Workload",
    "WorkloadStatus",
    "WorkloadThresholds",
    "DEFAULT_BASE_CAPACITY",
]
