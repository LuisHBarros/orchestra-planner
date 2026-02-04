"""Project configuration for business rules and constraints."""

from dataclasses import dataclass, field
from decimal import Decimal

from backend.src.domain.entities.workload import DEFAULT_BASE_CAPACITY


@dataclass(frozen=True)
class WorkloadThresholds:
    """
    Workload ratio thresholds for status classification (BR-WORK-003).

    Default thresholds:
    - Idle: ≤ 0.3
    - Relaxed: 0.3 < ratio ≤ 0.7
    - Healthy: 0.7 < ratio ≤ 1.2
    - Tight: 1.2 < ratio ≤ 1.5
    - Impossible: > 1.5
    """

    idle_max: Decimal = Decimal("0.3")
    relaxed_max: Decimal = Decimal("0.7")
    healthy_max: Decimal = Decimal("1.2")
    tight_max: Decimal = Decimal("1.5")

    def __post_init__(self) -> None:
        """Validate thresholds are in ascending order."""
        if not (self.idle_max < self.relaxed_max < self.healthy_max < self.tight_max):
            raise ValueError("Workload thresholds must be in ascending order")


@dataclass(frozen=True)
class ProjectConfig:
    """
    Centralized configuration for project-level business rules.

    This configuration controls:
    - BR-ASSIGN-003: Workload capacity and thresholds
    - BR-ASSIGN-004: Multitasking enablement
    - BR-PROJ-002: Manager task selection restrictions

    Initially uses sensible defaults but can be customized per-project
    in future iterations.
    """

    # BR-ASSIGN-003: Base capacity for workload calculation (story points)
    base_capacity: Decimal = field(default=DEFAULT_BASE_CAPACITY)

    # BR-WORK-003: Workload thresholds for status classification
    workload_thresholds: WorkloadThresholds = field(default_factory=WorkloadThresholds)

    # BR-ASSIGN-004: Whether employees can work on multiple tasks simultaneously
    # Default: False (single-task focus)
    allow_multitasking: bool = False

    # BR-PROJ-002: Whether managers are prevented from selecting tasks
    # Default: True (managers focus on planning, not execution)
    managers_cannot_select_tasks: bool = True

    # BR-DEP-003: Whether to automatically block tasks with unfinished dependencies
    enforce_dependency_blocking: bool = True

    @classmethod
    def default(cls) -> "ProjectConfig":
        """Create a ProjectConfig with default values."""
        return cls()

    @property
    def max_workload_ratio(self) -> Decimal:
        """Maximum workload ratio before task selection is blocked."""
        return self.workload_thresholds.tight_max
