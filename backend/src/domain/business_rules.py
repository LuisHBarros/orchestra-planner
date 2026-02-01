"""
Business rules definitions for Orchestra Planner.

This module provides a structured way to define and reference business rules
throughout the codebase. Each rule has a unique identifier that maps to the
rules documented in business_rules.md.

Usage:
    from domain.business_rules import BusinessRule, RuleCategory

    # Define a rule
    BR_TASK_004 = BusinessRule(
        category=RuleCategory.TASK,
        number=4,
        description="A Task cannot be selected if its Difficulty is not set",
    )

    # Reference in validation
    if task.difficulty_points is None:
        raise BR_TASK_004.violation("Task must have difficulty points set")
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class RuleCategory(str, Enum):
    """Categories of business rules as defined in business_rules.md."""

    AUTH = "AUTH"  # Authentication & Identity
    PROJ = "PROJ"  # Project Governance
    ROLE = "ROLE"  # Roles & Seniority
    INV = "INV"  # Invitations
    TASK = "TASK"  # Task Lifecycle
    DEP = "DEP"  # Dependencies
    ASSIGN = "ASSIGN"  # Assignment & Selection
    WORK = "WORK"  # Workload Calculation
    ABANDON = "ABANDON"  # Task Abandonment
    SCHED = "SCHED"  # Scheduling & Time
    LLM = "LLM"  # AI Integration
    NOTIF = "NOTIF"  # Notifications


class BusinessRuleViolation(Exception):
    """
    Exception raised when a business rule is violated.

    Attributes:
        rule: The business rule that was violated.
        message: Human-readable description of the violation.
        context: Optional additional context about the violation.
    """

    def __init__(
        self,
        rule: "BusinessRule",
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.rule = rule
        self.message = message
        self.context = context or {}
        super().__init__(f"[{rule.rule_id}] {message}")


@dataclass(frozen=True)
class BusinessRule:
    """
    Represents a business rule in the Orchestra Planner domain.

    Business rules are immutable value objects that define constraints and
    invariants in the domain. They provide a consistent way to:
    - Identify rules by their unique ID (e.g., BR-TASK-003)
    - Document rule descriptions
    - Create standardized violation exceptions

    Attributes:
        category: The category this rule belongs to (e.g., TASK, AUTH).
        number: The unique number within the category.
        description: Human-readable description of the rule.

    Example:
        BR_AUTH_002 = BusinessRule(
            category=RuleCategory.AUTH,
            number=2,
            description="Magic Link is valid for one-time use and expires after 15 minutes",
        )

        # Check and raise violation
        if link.is_expired():
            raise BR_AUTH_002.violation("Magic link has expired")
    """

    category: RuleCategory
    number: int
    description: str

    @property
    def rule_id(self) -> str:
        """
        Get the unique rule identifier.

        Returns:
            Rule ID in format BR-{CATEGORY}-{NUMBER:03d} (e.g., BR-TASK-003).
        """
        return f"BR-{self.category.value}-{self.number:03d}"

    def violation(
        self,
        message: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> BusinessRuleViolation:
        """
        Create a violation exception for this rule.

        Args:
            message: Custom message describing the violation.
                    Defaults to the rule description if not provided.
            context: Optional dictionary with additional context.

        Returns:
            A BusinessRuleViolation exception ready to be raised.

        Example:
            raise BR_TASK_004.violation("Cannot select task without difficulty")
        """
        return BusinessRuleViolation(
            rule=self,
            message=message or self.description,
            context=context,
        )

    def __str__(self) -> str:
        return f"{self.rule_id}: {self.description}"
