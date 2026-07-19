from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User

pytestmark = pytest.mark.django_db

GOOGLE_LOGIN_URL = "/api/v1/auth/google/login"
LOGOUT_URL = "/api/v1/auth/logout"
REFRESH_URL = "/api/v1/auth/refresh"


def _google_claims(**overrides):
    claims = {
        "sub": "google-uid-123",
        "email": "newanalyst@example.com",
        "email_verified": True,
        "given_name": "Jane",
        "family_name": "Doe",
        "picture": "https://example.com/photo.jpg",
    }
    claims.update(overrides)
    return claims


@patch("apps.authentication.services.google_id_token.verify_oauth2_token")
def test_google_login_success_creates_user(mock_verify, api_client):
    mock_verify.return_value = _google_claims()

    response = api_client.post(
        GOOGLE_LOGIN_URL,
        {"id_token": "valid-token", "phone_number": "+919876543210", "user_type": "ANALYST"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["success"] is True
    assert "access" in body["data"]
    assert "refresh" in body["data"]
    assert body["data"]["user"]["email"] == "newanalyst@example.com"
    assert User.objects.filter(google_id="google-uid-123").exists()


@patch("apps.authentication.services.google_id_token.verify_oauth2_token")
def test_google_login_failure_invalid_token(mock_verify, api_client):
    mock_verify.side_effect = ValueError("Token expired")

    response = api_client.post(
        GOOGLE_LOGIN_URL,
        {"id_token": "bad-token", "phone_number": "+919876543210", "user_type": "ANALYST"},
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_TOKEN"


def test_google_login_missing_phone_number(api_client):
    response = api_client.post(
        GOOGLE_LOGIN_URL,
        {"id_token": "some-token", "user_type": "ANALYST"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_google_login_missing_user_type(api_client):
    response = api_client.post(
        GOOGLE_LOGIN_URL,
        {"id_token": "some-token", "phone_number": "+919876543210"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@patch("apps.authentication.services.google_id_token.verify_oauth2_token")
def test_google_login_existing_user_logs_in_without_duplicating(
    mock_verify, api_client, analyst_user
):
    mock_verify.return_value = _google_claims(sub=analyst_user.google_id, email=analyst_user.email)

    response = api_client.post(
        GOOGLE_LOGIN_URL,
        {"id_token": "valid-token", "phone_number": "+919876543210", "user_type": "ANALYST"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert User.objects.filter(email=analyst_user.email).count() == 1


def test_logout_blacklists_refresh_token(api_client, analyst_user):
    refresh = RefreshToken.for_user(analyst_user)

    response = api_client.post(LOGOUT_URL, {"refresh": str(refresh)}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    reuse_response = api_client.post(REFRESH_URL, {"refresh": str(refresh)}, format="json")
    assert reuse_response.status_code == status.HTTP_400_BAD_REQUEST


def test_refresh_returns_new_access_token(api_client, analyst_user):
    refresh = RefreshToken.for_user(analyst_user)

    response = api_client.post(REFRESH_URL, {"refresh": str(refresh)}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.json()["data"]


def test_refresh_rejects_invalid_jwt(api_client):
    response = api_client.post(REFRESH_URL, {"refresh": "not-a-real-token"}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["error"]["code"] == "TOKEN_EXPIRED"


def test_expired_jwt_rejected_on_protected_endpoint(api_client, user_factory):
    from datetime import timedelta

    from rest_framework_simplejwt.tokens import AccessToken

    user = user_factory()
    access = AccessToken.for_user(user)
    access.set_exp(lifetime=timedelta(seconds=-1))

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    response = api_client.get("/api/v1/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
