import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.services import AuthenticationService, TokenService
from apps.users.services import InvitationService, UserService
from core.constants.choices import MemberStatus, UserRole
from core.exceptions.exceptions import (
    AccountPendingError,
    AccountSuspendedError,
    AlreadyRegisteredError,
    InvalidCredentialsError,
    NotInvitedError,
    ServiceError,
)

pytestmark = pytest.mark.django_db


def test_signup_rejects_uninvited_phone_number():
    with pytest.raises(NotInvitedError):
        AuthenticationService.signup(phone_number="+919876522001", pin="123456", name="X")


def test_signup_succeeds_for_invited_phone_number(admin_user):
    InvitationService.invite(admin_user, "+919876522002", UserRole.MEMBER)

    result = AuthenticationService.signup(phone_number="+919876522002", pin="123456", name="Ravi")

    assert result["user"].status == MemberStatus.ACTIVE
    assert result["user"].name == "Ravi"
    assert set(result.keys()) >= {"access", "refresh", "user"}


def test_signup_rejects_already_registered_phone_number(member_user):
    with pytest.raises(AlreadyRegisteredError):
        AuthenticationService.signup(phone_number=member_user.phone_number, pin="123456", name="X")


def test_login_rejects_unknown_phone_number():
    with pytest.raises(InvalidCredentialsError):
        AuthenticationService.login(phone_number="+919999999999", pin="123456")


def test_login_rejects_wrong_pin(user_factory):
    user = user_factory(pin="123456")
    with pytest.raises(InvalidCredentialsError):
        AuthenticationService.login(phone_number=user.phone_number, pin="000000")


def test_login_succeeds_with_correct_pin(user_factory):
    user = user_factory(pin="123456")
    result = AuthenticationService.login(phone_number=user.phone_number, pin="123456")
    assert result["user"] == user


def test_login_rejects_pending_member(user_factory):
    user = user_factory(status=MemberStatus.PENDING, is_active=False)
    with pytest.raises(AccountPendingError):
        AuthenticationService.login(phone_number=user.phone_number, pin="123456")


def test_login_rejects_suspended_member(admin_user, member_user):
    UserService.suspend(admin_user, member_user, "policy violation")
    with pytest.raises(AccountSuspendedError):
        AuthenticationService.login(phone_number=member_user.phone_number, pin="123456")


def test_change_pin_updates_password(user_factory):
    user = user_factory(pin="123456")
    AuthenticationService.change_pin(user, "123456", "654321")
    assert user.check_password("654321") is True


def test_change_pin_rejects_wrong_old_pin(user_factory):
    user = user_factory(pin="123456")
    with pytest.raises(InvalidCredentialsError):
        AuthenticationService.change_pin(user, "000000", "654321")


def test_issue_tokens_for_user_returns_access_and_refresh(user_factory):
    user = user_factory()
    tokens = TokenService.issue_tokens_for_user(user)

    assert set(tokens.keys()) == {"access", "refresh"}


def test_blacklist_token_rejects_garbage_token():
    with pytest.raises(ServiceError):
        TokenService.blacklist_token("not-a-real-token")


def test_refresh_access_token_returns_new_access(user_factory):
    user = user_factory()
    refresh = RefreshToken.for_user(user)

    result = TokenService.refresh_access_token(str(refresh))

    assert "access" in result
