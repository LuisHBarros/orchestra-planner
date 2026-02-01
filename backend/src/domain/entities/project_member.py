"""ProjectMember entity definition."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .seniority_level import SeniorityLevel


@dataclass
class ProjectMember:
    """
    Represents a User's membership in a Project with a specific Role and Seniority.
    
    This is the context of a User within a Project (Employee).
    
    BR-ROLE-002: Every Employee must have exactly one Role per Project.
    BR-ROLE-003: Every Employee must have a Seniority Level.
    """
    project_id: UUID
    user_id: UUID
    role_id: UUID
    seniority_level: SeniorityLevel
    id: UUID = field(default_factory=uuid4)
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProjectMember):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def update_role(self, role_id: UUID) -> None:
        """Update the member's role within the project."""
        self.role_id = role_id

    def update_seniority(self, seniority_level: SeniorityLevel) -> None:
        """Update the member's seniority level."""
        self.seniority_level = seniority_level
