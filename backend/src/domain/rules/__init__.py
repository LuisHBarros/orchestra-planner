"""
Business rules catalog for Orchestra Planner.

This module exports all defined business rules organized by category.
Import rules directly to use them in domain logic:

    from domain.rules import BR_TASK_004

    if task.difficulty_points is None:
        raise BR_TASK_004.violation("Task difficulty must be set before selection")
"""

from .task_rules import (
    BR_TASK_001,
    BR_TASK_002,
    BR_TASK_003,
    BR_TASK_004,
)

__all__ = [
    # Task rules
    "BR_TASK_001",
    "BR_TASK_002",
    "BR_TASK_003",
    "BR_TASK_004",
]
