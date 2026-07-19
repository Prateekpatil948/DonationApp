import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

ME_URL = "/api/v1/users/me"


def test_profile_fetch_requires_authentication(api_client):
    response = api_client.get(ME_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_profile_fetch_returns_current_user(authenticated_client):
    client, user = authenticated_client

    response = client.get(ME_URL)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == user.email
    assert body["data"]["user_type"] == user.user_type


def test_profile_update_editable_fields(authenticated_client):
    client, user = authenticated_client

    response = client.put(
        ME_URL,
        {
            "first_name": "Updated",
            "last_name": "Name",
            "phone_number": "+919999999999",
            "profile_picture": "https://example.com/new.jpg",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["data"]["first_name"] == "Updated"
    assert body["data"]["phone_number"] == "+919999999999"

    user.refresh_from_db()
    assert user.first_name == "Updated"


def test_profile_update_ignores_non_editable_fields(authenticated_client):
    client, user = authenticated_client
    original_email = user.email

    response = client.put(
        ME_URL,
        {"email": "hacker@example.com", "user_type": "SUBSCRIBER"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.email == original_email
    assert user.user_type == "ANALYST"


def test_profile_update_validation_failure_on_bad_phone(authenticated_client):
    client, _ = authenticated_client

    response = client.put(ME_URL, {"phone_number": "not-a-phone"}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_subscriber_cannot_access_analyst_only_permission(subscriber_user, api_client):
    from core.permissions.roles import IsAnalyst

    class FakeRequest:
        user = subscriber_user

    assert IsAnalyst().has_permission(FakeRequest(), None) is False
