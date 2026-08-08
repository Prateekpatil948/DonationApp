import pytest

from apps.users.services import InvitationService, UserService
from core.constants.choices import InvitationStatus, MemberStatus, UserRole
from core.exceptions.exceptions import DuplicateInvitationError

pytestmark = pytest.mark.django_db


def test_update_profile_only_touches_editable_fields(user_factory):
    user = user_factory(name="Old", phone_number="+919876500010")

    updated = UserService.update_profile(user, {"name": "New"})

    assert updated.name == "New"
    assert updated.phone_number == "+919876500010"


def test_invite_creates_pending_user_and_invitation(admin_user):
    invitation = InvitationService.invite(admin_user, "+919876500020", UserRole.MEMBER)

    assert invitation.status == InvitationStatus.PENDING
    user = UserService.get_by_phone_number("+919876500020")
    assert user is not None
    assert user.status == MemberStatus.PENDING
    assert user.has_usable_password() is False


def test_invite_rejects_duplicate_pending_invitation(admin_user):
    InvitationService.invite(admin_user, "+919876500030", UserRole.MEMBER)
    with pytest.raises(DuplicateInvitationError):
        InvitationService.invite(admin_user, "+919876500030", UserRole.MEMBER)


def test_invite_rejects_already_active_phone_number(admin_user, member_user):
    with pytest.raises(DuplicateInvitationError):
        InvitationService.invite(admin_user, member_user.phone_number, UserRole.MEMBER)


def test_suspend_then_reactivate_round_trip(admin_user, member_user):
    suspended = UserService.suspend(admin_user, member_user, "Policy violation")
    assert suspended.status == MemberStatus.SUSPENDED
    assert suspended.is_active is False
    assert suspended.suspension_reason == "Policy violation"

    reactivated = UserService.reactivate(admin_user, suspended, "Resolved")
    assert reactivated.status == MemberStatus.ACTIVE
    assert reactivated.is_active is True
    assert reactivated.suspension_reason == ""


def test_deactivate_sets_inactive_status(admin_user, member_user):
    deactivated = UserService.deactivate(admin_user, member_user, "No longer volunteering")
    assert deactivated.status == MemberStatus.INACTIVE
    assert deactivated.is_active is False


def test_list_members_filters_by_status_and_search(admin_user, member_user):
    results = UserService.list_members({"status": MemberStatus.ACTIVE, "search": member_user.name})
    assert member_user in results
