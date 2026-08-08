import pytest
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.services import InvitationService
from core.constants.choices import UserRole

pytestmark = pytest.mark.django_db

SIGNUP_URL = "/api/v1/auth/signup"
LOGIN_URL = "/api/v1/auth/login"
LOGOUT_URL = "/api/v1/auth/logout"
REFRESH_URL = "/api/v1/auth/refresh"
CHANGE_PIN_URL = "/api/v1/auth/change-pin"


def test_signup_succeeds_for_invited_phone_number(api_client, admin_user):
    InvitationService.invite(admin_user, "+919876533001", UserRole.MEMBER)

    response = api_client.post(
        SIGNUP_URL,
        {
            "phone_number": "+919876533001",
            "pin": "123456",
            "confirm_pin": "123456",
            "name": "Ravi Kumar",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "access" in body["data"]
    assert body["data"]["user"]["name"] == "Ravi Kumar"


def test_signup_rejects_mismatched_pin_confirmation(api_client, admin_user):
    InvitationService.invite(admin_user, "+919876533002", UserRole.MEMBER)

    response = api_client.post(
        SIGNUP_URL,
        {
            "phone_number": "+919876533002",
            "pin": "123456",
            "confirm_pin": "654321",
            "name": "X",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_signup_rejects_uninvited_phone_number(api_client):
    response = api_client.post(
        SIGNUP_URL,
        {"phone_number": "+919876533003", "pin": "123456", "confirm_pin": "123456", "name": "X"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["error"]["code"] == "NOT_INVITED"


def test_login_success(api_client, user_factory):
    user = user_factory(pin="123456")

    response = api_client.post(
        LOGIN_URL, {"phone_number": user.phone_number, "pin": "123456"}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.json()["data"]


def test_login_failure_wrong_pin(api_client, user_factory):
    user = user_factory(pin="123456")

    response = api_client.post(
        LOGIN_URL, {"phone_number": user.phone_number, "pin": "000000"}, format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_logout_blacklists_refresh_token(api_client, member_user):
    refresh = RefreshToken.for_user(member_user)

    response = api_client.post(LOGOUT_URL, {"refresh": str(refresh)}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    reuse_response = api_client.post(REFRESH_URL, {"refresh": str(refresh)}, format="json")
    assert reuse_response.status_code == status.HTTP_400_BAD_REQUEST


def test_refresh_returns_new_access_token(api_client, member_user):
    refresh = RefreshToken.for_user(member_user)

    response = api_client.post(REFRESH_URL, {"refresh": str(refresh)}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.json()["data"]


def test_refresh_rejects_invalid_jwt(api_client):
    response = api_client.post(REFRESH_URL, {"refresh": "not-a-real-token"}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["error"]["code"] == "TOKEN_EXPIRED"


def test_change_pin_success(authenticated_client):
    client, user = authenticated_client
    user.set_password("123456")
    user.save(update_fields=["password"])

    response = client.post(
        CHANGE_PIN_URL, {"old_pin": "123456", "new_pin": "654321"}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.check_password("654321") is True


def test_expired_jwt_rejected_on_protected_endpoint(api_client, user_factory):
    from datetime import timedelta

    from rest_framework_simplejwt.tokens import AccessToken

    user = user_factory()
    access = AccessToken.for_user(user)
    access.set_exp(lifetime=timedelta(seconds=-1))

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    response = api_client.get("/api/v1/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_model_has_no_google_fields():
    assert not hasattr(User, "google_id")
