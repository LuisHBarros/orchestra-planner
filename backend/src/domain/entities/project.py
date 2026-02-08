"""Project entity definition."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from backend.src.domain.time import utcnow


@dataclass
class Project:
    """
    A collaborative workspace containing Tasks and Members.

    BR-PROJ-001: The User who creates a Project is automatically assigned as the Manager.
    BR-PROJ-003: Project's "Expected End Date" is dynamic, calculated from critical path.
    BR-PROJ-004: Only the Manager can edit Project settings.
    """

    name: str
    manager_id: UUID
    id: UUID = field(default_factory=uuid4)
    description: str = field(default="")
    llm_provider: str | None = field(default=None)
    llm_api_key_encrypted: str | None = field(default=None)
    expected_end_date: datetime | None = field(default=None)
    created_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        """Validate project attributes."""
        if not self.name or not self.name.strip():
            raise ValueError("Project name cannot be empty")
        self.name = self.name.strip()
        if self.description:
            self.description = self.description.strip()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Project):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def is_llm_enabled(self) -> bool:
        """Check if LLM features are enabled for this project (BR-LLM-001)."""
        return bool(self.llm_provider and self.llm_api_key_encrypted)

    def configure_llm(self, provider: str, encrypted_api_key: str) -> None:
        """
        Configure LLM settings for the project.

        BR-LLM-001: LLM features are optional and per-project.
        BR-LLM-002: API Keys must be stored encrypted.
        """
        if not provider or not provider.strip():
            raise ValueError("LLM provider cannot be empty")
        if not encrypted_api_key:
            raise ValueError("Encrypted API key cannot be empty")
        self.llm_provider = provider.strip()
        self.llm_api_key_encrypted = encrypted_api_key

    def disable_llm(self) -> None:
        """Disable LLM features for this project."""
        self.llm_provider = None
        self.llm_api_key_encrypted = None

    def update_expected_end_date(self, end_date: datetime | None) -> None:
        """
        Update the expected end date (BR-PROJ-003).

        This is typically called by the scheduling system after recalculating
        the critical path of tasks.
        """
        self.expected_end_date = end_date

    def is_manager(self, user_id: UUID) -> bool:
        """Check if a user is the manager of this project."""
        return self.manager_id == user_id
