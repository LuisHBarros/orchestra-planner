"""Accept invite use case."""

from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities import ProjectMember, SeniorityLevel
from backend.src.domain.errors import (
    InviteAlreadyAcceptedError,
    InviteExpiredError,
    InviteNotFoundError,
    UserAlreadyMemberError,
    UserNotFoundError,
)
from backend.src.domain.ports.unit_of_work import UnitOfWork


@dataclass
class AcceptInviteInput:
    """Input for accepting a project invitation."""

    token: str
    user_id: UUID
    seniority_level: SeniorityLevel = SeniorityLevel.MID


@dataclass
class AcceptInviteOutput:
    """Output containing the created membership."""

    member: ProjectMember


class AcceptInviteUseCase:
    """Use case for accepting a project invitation."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, input: AcceptInviteInput) -> AcceptInviteOutput:
        """
        Accept a project invitation and become a member.

        BR-INV-004: An invite has three states: Pending, Accepted, Expired.
        BR-INV-005: A User cannot accept an invite if already a member.

        Raises:
            InviteNotFoundError: If invite doesn't exist.
            InviteExpiredError: If invite has expired.
            InviteAlreadyAcceptedError: If invite was already accepted.
            UserNotFoundError: If user doesn't exist.
            UserAlreadyMemberError: If user is already a project member.
        """
        async with self.uow:
            invite = await self.uow.project_invite_repository.find_by_token(input.token)
            if invite is None:
                raise InviteNotFoundError(input.token)

            # Check and update expiration status
            invite.check_and_update_expiration()

            if not invite.is_valid:
                if invite.status.value == "Accepted":
                    raise InviteAlreadyAcceptedError(input.token)
                raise InviteExpiredError(input.token)

            # Verify user exists
            user = await self.uow.user_repository.find_by_id(input.user_id)
            if user is None:
                raise UserNotFoundError(str(input.user_id))

            # BR-INV-005: Check if user is already a member
            existing_member = (
                await self.uow.project_member_repository.find_by_project_and_user(
                    invite.project_id, input.user_id
                )
            )
            if existing_member is not None:
                raise UserAlreadyMemberError(str(input.user_id), str(invite.project_id))

            # Accept the invite
            invite.accept()
            await self.uow.project_invite_repository.save(invite)

            # Create the membership
            member = ProjectMember(
                project_id=invite.project_id,
                user_id=input.user_id,
                role_id=invite.role_id,
                seniority_level=input.seniority_level,
            )
            await self.uow.project_member_repository.save(member)

            await self.uow.commit()

        return AcceptInviteOutput(member=member)
