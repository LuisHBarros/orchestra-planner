"""Tests for ConfigureProjectLLMUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.project_management import (
    ConfigureProjectLLMInput,
    ConfigureProjectLLMUseCase,
)
from backend.src.domain.entities import Project
from backend.src.domain.errors import ManagerRequiredError, ProjectNotFoundError


@pytest.fixture
def project_repository():
    return AsyncMock()


@pytest.fixture
def encryption_service():
    return AsyncMock()


@pytest.fixture
def use_case(project_repository, encryption_service):
    return ConfigureProjectLLMUseCase(
        project_repository=project_repository,
        encryption_service=encryption_service,
    )


@pytest.fixture
def manager_id():
    return uuid4()


@pytest.fixture
def existing_project(manager_id):
    return Project(name="Test Project", manager_id=manager_id)


class TestConfigureProjectLLMUseCase:
    """Tests for ConfigureProjectLLMUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_configures_llm_when_requester_is_manager(
        self,
        use_case,
        project_repository,
        encryption_service,
        existing_project,
        manager_id,
    ):
        """BR-LLM-001: LLM features are optional and per-project."""
        project_repository.find_by_id.return_value = existing_project
        encryption_service.encrypt.return_value = "encrypted_key_123"
        project_repository.save.return_value = None

        input_data = ConfigureProjectLLMInput(
            project_id=existing_project.id,
            requester_id=manager_id,
            provider="openai",
            api_key="sk-test-key-123",
        )

        await use_case.execute(input_data)

        assert existing_project.llm_provider == "openai"
        assert existing_project.llm_api_key_encrypted == "encrypted_key_123"
        project_repository.save.assert_called_once_with(existing_project)

    @pytest.mark.asyncio
    async def test_encrypts_api_key_before_storing(
        self,
        use_case,
        project_repository,
        encryption_service,
        existing_project,
        manager_id,
    ):
        """BR-LLM-002: API Keys must be stored encrypted."""
        project_repository.find_by_id.return_value = existing_project
        encryption_service.encrypt.return_value = "encrypted_secret"
        project_repository.save.return_value = None

        input_data = ConfigureProjectLLMInput(
            project_id=existing_project.id,
            requester_id=manager_id,
            provider="anthropic",
            api_key="plain_text_key",
        )

        await use_case.execute(input_data)

        encryption_service.encrypt.assert_called_once_with("plain_text_key")
        assert existing_project.llm_api_key_encrypted == "encrypted_secret"

    @pytest.mark.asyncio
    async def test_raises_project_not_found_when_project_does_not_exist(
        self, use_case, project_repository, encryption_service
    ):
        """Should raise ProjectNotFoundError when project doesn't exist."""
        project_repository.find_by_id.return_value = None
        project_id = uuid4()
        requester_id = uuid4()

        input_data = ConfigureProjectLLMInput(
            project_id=project_id,
            requester_id=requester_id,
            provider="openai",
            api_key="sk-test-key",
        )

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(input_data)

        encryption_service.encrypt.assert_not_called()
        project_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_manager_required_when_requester_is_not_manager(
        self, use_case, project_repository, encryption_service, existing_project
    ):
        """BR-PROJ-004: Only the Manager can edit Project settings."""
        project_repository.find_by_id.return_value = existing_project
        non_manager_id = uuid4()

        input_data = ConfigureProjectLLMInput(
            project_id=existing_project.id,
            requester_id=non_manager_id,
            provider="openai",
            api_key="sk-test-key",
        )

        with pytest.raises(ManagerRequiredError):
            await use_case.execute(input_data)

        encryption_service.encrypt.assert_not_called()
        project_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_enables_llm_features_after_configuration(
        self,
        use_case,
        project_repository,
        encryption_service,
        existing_project,
        manager_id,
    ):
        """Project should have LLM enabled after configuration."""
        project_repository.find_by_id.return_value = existing_project
        encryption_service.encrypt.return_value = "encrypted_key"
        project_repository.save.return_value = None

        assert existing_project.is_llm_enabled is False

        input_data = ConfigureProjectLLMInput(
            project_id=existing_project.id,
            requester_id=manager_id,
            provider="openai",
            api_key="sk-test-key",
        )

        await use_case.execute(input_data)

        assert existing_project.is_llm_enabled is True

    @pytest.mark.asyncio
    async def test_saves_project_after_configuration(
        self,
        use_case,
        project_repository,
        encryption_service,
        existing_project,
        manager_id,
    ):
        """Should persist the project with new LLM settings."""
        project_repository.find_by_id.return_value = existing_project
        encryption_service.encrypt.return_value = "encrypted_key"
        project_repository.save.return_value = None

        input_data = ConfigureProjectLLMInput(
            project_id=existing_project.id,
            requester_id=manager_id,
            provider="openai",
            api_key="sk-test-key",
        )

        await use_case.execute(input_data)

        project_repository.save.assert_called_once()
        saved_project = project_repository.save.call_args[0][0]
        assert saved_project.llm_provider == "openai"
        assert saved_project.llm_api_key_encrypted == "encrypted_key"
