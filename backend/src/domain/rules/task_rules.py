"""
Task lifecycle business rules (BR-TASK).

These rules govern task creation, modification, status transitions, and selection.
Reference: business_rules.md section BR-TASK.
"""

from backend.src.domain.business_rules import BusinessRule, RuleCategory

BR_TASK_001 = BusinessRule(
    category=RuleCategory.TASK,
    number=1,
    description="Only the Manager can create, edit, or delete Tasks",
)

BR_TASK_002 = BusinessRule(
    category=RuleCategory.TASK,
    number=2,
    description="A Task must have a numeric Difficulty (Story Points)",
)

BR_TASK_003 = BusinessRule(
    category=RuleCategory.TASK,
    number=3,
    description="Task Status Transitions are strict",
)

BR_TASK_004 = BusinessRule(
    category=RuleCategory.TASK,
    number=4,
    description="A Task cannot be selected (Doing) if its Difficulty is not set",
)
