"""Tests for AcceptInviteUseCase."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.invitations import (
    AcceptInviteInput,
    AcceptInviteUseCase,
)
from backend.src.domain.entities import (
    InviteStatus,
    ProjectInvite,
    ProjectMember,
    SeniorityLevel,
    User,
)
from backend.src.domain.errors import (
    InviteAlreadyAcceptedError,
    InviteExpiredError,
    InviteNotFoundError,
    UserAlreadyMemberError,
    UserNotFoundError,
)


@pytest.fixture
def uow():
    mock = AsyncMock()
    mock.user_repository = AsyncMock()
    mock.project_invite_repository = AsyncMock()
    mock.project_member_repository = AsyncMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def use_case(uow):
    return AcceptInviteUseCase(uow=uow)


@pytest.fixture
def project_id():
    return uuid4()


@pytest.fixture
def role_id():
    return uuid4()


@pytest.fixture
def manager_id():
    return uuid4()


@pytest.fixture
def valid_invite(project_id, role_id, manager_id):
    return ProjectInvite(
        project_id=project_id,
        role_id=role_id,
        created_by=manager_id,
    )


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def existing_user(user_id):
    return User(email="user@example.com", name="Test User")


class TestAcceptInviteUseCase:
    """Tests for AcceptInviteUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_accepts_invite_successfully(
        self,
        use_case,
        uow,
        valid_invite,
        existing_user,
        user_id,
    ):
        """User can accept a valid invite."""
        uow.project_invite_repository.find_by_token.return_value = valid_invite
        uow.user_repository.find_by_id.return_value = existing_user
        uow.project_member_repository.find_by_project_and_user.return_value = None
        uow.project_invite_repository.save.return_value = None
        uow.project_member_repository.save.return_value = None

        input_data = AcceptInviteInput(
            token=valid_invite.token,
            user_id=user_id,
            seniority_level=SeniorityLevel.MID,
        )

        result = await use_case.execute(input_data)

        assert result.member.project_id == valid_invite.project_id
        assert result.member.user_id == user_id
        assert result.member.role_id == valid_invite.role_id
        assert result.member.seniority_level == SeniorityLevel.MID
        uow.project_member_repository.save.assert_called_once()
        uow.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_accepts_invite_with_custom_seniority(
        self,
        use_case,
        uow,
        valid_invite,
        existing_user,
        user_id,
    ):
        """User can specify their seniority level when accepting."""
        uow.project_invite_repository.find_by_token.return_value = valid_invite
        uow.user_repository.find_by_id.return_value = existing_user
        uow.project_member_repository.find_by_project_and_user.return_value = None
        uow.project_invite_repository.save.return_value = None
        uow.project_member_repository.save.return_value = None

        input_data = AcceptInviteInput(
            token=valid_invite.token,
            user_id=user_id,
            seniority_level=SeniorityLevel.SENIOR,
        )

        result = await use_case.execute(input_data)

        assert result.member.seniority_level == SeniorityLevel.SENIOR

    @pytest.mark.asyncio
    async def test_invite_status_changes_to_accepted(
        self,
        use_case,
        uow,
        valid_invite,
        existing_user,
        user_id,
    ):
        """BR-INV-004: Invite status changes to Accepted."""
        uow.project_invite_repository.find_by_token.return_value = valid_invite
        uow.user_repository.find_by_id.return_value = existing_user
        uow.project_member_repository.find_by_project_and_user.return_value = None
        uow.project_invite_repository.save.return_value = None
        uow.project_member_repository.save.return_value = None

        input_data = AcceptInviteInput(
            token=valid_invite.token,
            user_id=user_id,
        )

        await use_case.execute(input_data)

        assert valid_invite.status == InviteStatus.ACCEPTED
        uow.project_invite_repository.save.assert_called()

    @pytest.mark.asyncio
    async def test_raises_invite_not_found(
        self,
        use_case,
        uow,
    ):
        """Should raise InviteNotFoundError when invite doesn't exist."""
        uow.project_invite_repository.find_by_token.return_value = None

        input_data = AcceptInviteInput(
            token="invalid-token",
            user_id=uuid4(),
        )

        with pytest.raises(InviteNotFoundError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_invite_expired(
        self,
        use_case,
        uow,
        project_id,
        role_id,
        manager_id,
    ):
        """BR-INV-004: Should raise InviteExpiredError when invite has expired."""
        expired_invite = ProjectInvite(
            project_id=project_id,
            role_id=role_id,
            created_by=manager_id,
        )
        # Manually expire the invite
        expired_invite.expires_at = datetime.now(timezone.utc) - timedelta(days=1)

        uow.project_invite_repository.find_by_token.return_value = expired_invite

        input_data = AcceptInviteInput(
            token=expired_invite.token,
            user_id=uuid4(),
        )

        with pytest.raises(InviteExpiredError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_invite_already_accepted(
        self,
        use_case,
        uow,
        project_id,
        role_id,
        manager_id,
    ):
        """BR-INV-004: Should raise InviteAlreadyAcceptedError when already accepted."""
        accepted_invite = ProjectInvite(
            project_id=project_id,
            role_id=role_id,
            created_by=manager_id,
        )
        accepted_invite.accept()  # Mark as accepted

        uow.project_invite_repository.find_by_token.return_value = accepted_invite

        input_data = AcceptInviteInput(
            token=accepted_invite.token,
            user_id=uuid4(),
        )

        with pytest.raises(InviteAlreadyAcceptedError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_user_not_found(
        self,
        use_case,
        uow,
        valid_invite,
    ):
        """Should raise UserNotFoundError when user doesn't exist."""
        uow.project_invite_repository.find_by_token.return_value = valid_invite
        uow.user_repository.find_by_id.return_value = None

        input_data = AcceptInviteInput(
            token=valid_invite.token,
            user_id=uuid4(),
        )

        with pytest.raises(UserNotFoundError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_user_already_member(
        self,
        use_case,
        uow,
        valid_invite,
        existing_user,
        user_id,
    ):
        """BR-INV-005: A User cannot accept an invite if already a member."""
        existing_membership = ProjectMember(
            project_id=valid_invite.project_id,
            user_id=user_id,
            role_id=uuid4(),
            seniority_level=SeniorityLevel.MID,
        )
        uow.project_invite_repository.find_by_token.return_value = valid_invite
        uow.user_repository.find_by_id.return_value = existing_user
        uow.project_member_repository.find_by_project_and_user.return_value = (
            existing_membership
        )

        input_data = AcceptInviteInput(
            token=valid_invite.token,
            user_id=user_id,
        )

        with pytest.raises(UserAlreadyMemberError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_creates_project_membership(
        self,
        use_case,
        uow,
        valid_invite,
        existing_user,
        user_id,
    ):
        """Should create a ProjectMember when accepting invite."""
        uow.project_invite_repository.find_by_token.return_value = valid_invite
        uow.user_repository.find_by_id.return_value = existing_user
        uow.project_member_repository.find_by_project_and_user.return_value = None
        uow.project_invite_repository.save.return_value = None
        uow.project_member_repository.save.return_value = None

        input_data = AcceptInviteInput(
            token=valid_invite.token,
            user_id=user_id,
        )

        await use_case.execute(input_data)

        uow.project_member_repository.save.assert_called_once()
        saved_member = uow.project_member_repository.save.call_args[0][0]
        assert isinstance(saved_member, ProjectMember)
        assert saved_member.project_id == valid_invite.project_id
        assert saved_member.role_id == valid_invite.role_id

    @pytest.mark.asyncio
    async def test_saves_both_invite_and_member(
        self,
        use_case,
        uow,
        valid_invite,
        existing_user,
        user_id,
    ):
        """Should save both the invite (updated status) and the new member."""
        uow.project_invite_repository.find_by_token.return_value = valid_invite
        uow.user_repository.find_by_id.return_value = existing_user
        uow.project_member_repository.find_by_project_and_user.return_value = None
        uow.project_invite_repository.save.return_value = None
        uow.project_member_repository.save.return_value = None

        input_data = AcceptInviteInput(
            token=valid_invite.token,
            user_id=user_id,
        )

        await use_case.execute(input_data)

        uow.project_invite_repository.save.assert_called_once()
        uow.project_member_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_does_not_commit_on_member_save_failure(
        self,
        use_case,
        uow,
        valid_invite,
        existing_user,
        user_id,
    ):
        """UoW should not commit if member save fails after invite update."""
        uow.project_invite_repository.find_by_token.return_value = valid_invite
        uow.user_repository.find_by_id.return_value = existing_user
        uow.project_member_repository.find_by_project_and_user.return_value = None
        uow.project_invite_repository.save.return_value = None
        uow.project_member_repository.save.side_effect = Exception("DB error")

        input_data = AcceptInviteInput(
            token=valid_invite.token,
            user_id=user_id,
        )

        with pytest.raises(Exception, match="DB error"):
            await use_case.execute(input_data)

        uow.commit.assert_not_called()
