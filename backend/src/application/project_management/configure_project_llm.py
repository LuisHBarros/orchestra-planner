from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.errors import (
    ManagerRequiredError,
    ProjectNotFoundError,
)
from backend.src.domain.ports import ProjectRepository
from backend.src.domain.ports.services import EncryptionService


@dataclass
class ConfigureProjectLLMInput:
    """Input for configuring project LLM settings."""

    project_id: UUID
    requester_id: UUID
    provider: str
    api_key: str  # Plain text, will be encrypted


class ConfigureProjectLLMUseCase:
    """Use case for configuring LLM settings on a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        encryption_service: EncryptionService,
    ):
        self.project_repository = project_repository
        self.encryption_service = encryption_service

    async def execute(self, input: ConfigureProjectLLMInput) -> None:
        """
        Configure LLM provider and API key for a project.

        BR-LLM-001: LLM features are optional and per-project.
        BR-LLM-002: API Keys must be stored encrypted.
        BR-PROJ-004: Only the Manager can edit Project settings.

        Raises:
            ProjectNotFoundError: If project doesn't exist.
            ManagerRequiredError: If requester is not the project manager.
        """
        project = await self.project_repository.find_by_id(input.project_id)
        if project is None:
            raise ProjectNotFoundError(str(input.project_id))

        if not project.is_manager(input.requester_id):
            raise ManagerRequiredError("configure LLM")

        encrypted_key = await self.encryption_service.encrypt(input.api_key)

        project.configure_llm(input.provider, encrypted_key)

        await self.project_repository.save(project)
