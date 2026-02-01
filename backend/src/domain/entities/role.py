"""Role entity definition."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class Role:
    """
    A job title defined within a Project.
    
    BR-ROLE-001: Roles are created by the Manager.
    BR-ROLE-002: Every Employee must have exactly one Role per Project.
    
    Examples: "Backend Developer", "Designer", "Frontend Developer"
    """
    project_id: UUID
    name: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate role attributes."""
        if not self.name or not self.name.strip():
            raise ValueError("Role name cannot be empty")
        self.name = self.name.strip()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
