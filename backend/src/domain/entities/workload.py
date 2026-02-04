"""Workload calculation and status definitions."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from .seniority_level import SeniorityLevel

if TYPE_CHECKING:
    from .task import Task


class WorkloadStatus(str, Enum):
    """
    Workload status thresholds as defined in BR-WORK-003.

    - Idle: Ratio ≤ 0.3
    - Relaxed: 0.3 < Ratio ≤ 0.7
    - Healthy: 0.7 < Ratio ≤ 1.2
    - Tight: 1.2 < Ratio ≤ 1.5
    - Impossible: Ratio > 1.5
    """

    IDLE = "Idle"
    RELAXED = "Relaxed"
    HEALTHY = "Healthy"
    TIGHT = "Tight"
    IMPOSSIBLE = "Impossible"


# Base capacity for workload calculation (story points per sprint/period)
DEFAULT_BASE_CAPACITY = Decimal("10")

# Default workload thresholds (BR-WORK-003)
DEFAULT_MAX_WORKLOAD_RATIO = Decimal("1.5")


@dataclass(frozen=True)
class Workload:
    """
    Value object representing an employee's workload calculation.

    BR-WORK-001: Workload Score = Sum of Difficulty of all tasks in Doing status.
    BR-WORK-002: Workload Ratio = Workload Score / (Base Capacity * Level Multiplier).

    This is a pure value object responsible for:
    - Calculating effective capacity based on seniority
    - Computing workload ratio
    - Determining workload status
    - Validating if additional points can be taken
    """

    score: Decimal
    base_capacity: Decimal
    seniority_level: SeniorityLevel

    @property
    def effective_capacity(self) -> Decimal:
        """Calculate effective capacity based on seniority level."""
        return self.base_capacity * self.seniority_level.capacity_multiplier

    @property
    def ratio(self) -> Decimal:
        """Calculate workload ratio."""
        if self.effective_capacity == 0:
            return Decimal("0")
        return self.score / self.effective_capacity

    @property
    def status(self) -> WorkloadStatus:
        """
        Determine workload status based on ratio thresholds (BR-WORK-003).
        """
        ratio = self.ratio
        if ratio <= Decimal("0.3"):
            return WorkloadStatus.IDLE
        elif ratio <= Decimal("0.7"):
            return WorkloadStatus.RELAXED
        elif ratio <= Decimal("1.2"):
            return WorkloadStatus.HEALTHY
        elif ratio <= Decimal("1.5"):
            return WorkloadStatus.TIGHT
        else:
            return WorkloadStatus.IMPOSSIBLE

    def can_take_additional_points(
        self,
        points: int,
        max_ratio: Decimal = DEFAULT_MAX_WORKLOAD_RATIO,
    ) -> bool:
        """
        Check if taking additional story points would exceed the max workload ratio.

        BR-ASSIGN-003: Employee cannot select task if it pushes workload to Impossible.

        Args:
            points: The story points of the task to potentially take
            max_ratio: Maximum allowed workload ratio (default: 1.5 for Impossible threshold)
        """
        new_score = self.score + Decimal(points)
        new_ratio = (
            new_score / self.effective_capacity
            if self.effective_capacity
            else Decimal("0")
        )
        return new_ratio <= max_ratio

    @property
    def remaining_capacity_points(self) -> int:
        """
        Calculate how many additional story points can be taken before hitting Impossible.

        Returns the maximum integer points that can be added while staying at or below 1.5 ratio.
        """
        max_score = self.effective_capacity * DEFAULT_MAX_WORKLOAD_RATIO
        remaining = max_score - self.score
        return max(0, int(remaining))

    @classmethod
    def calculate(
        cls,
        task_points: list[int],
        seniority_level: SeniorityLevel,
        base_capacity: Decimal = DEFAULT_BASE_CAPACITY,
    ) -> "Workload":
        """
        Factory method to calculate workload from a list of task difficulty points.

        Args:
            task_points: List of story points from tasks in Doing status
            seniority_level: The employee's seniority level
            base_capacity: The base capacity for calculations
        """
        score = Decimal(sum(task_points))
        return cls(
            score=score,
            base_capacity=base_capacity,
            seniority_level=seniority_level,
        )

    @classmethod
    def from_tasks(
        cls,
        tasks: list["Task"],
        seniority_level: SeniorityLevel,
        base_capacity: Decimal = DEFAULT_BASE_CAPACITY,
    ) -> "Workload":
        """
        Factory method to calculate workload directly from a list of Task entities.

        This is the preferred factory method as it encapsulates the logic for
        extracting relevant task data (only Doing tasks with difficulty points).

        BR-WORK-001: Only tasks in Doing status count toward workload score.

        Args:
            tasks: List of Task entities assigned to the employee
            seniority_level: The employee's seniority level
            base_capacity: The base capacity for calculations
        """
        from .task import TaskStatus

        points = [
            task.difficulty_points
            for task in tasks
            if task.status == TaskStatus.DOING and task.difficulty_points is not None
        ]
        return cls.calculate(points, seniority_level, base_capacity)
