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
    assert body["data"]["phone_number"] == user.phone_number
    assert body["data"]["role"] == user.role


def test_profile_update_editable_fields(authenticated_client):
    client, user = authenticated_client

    response = client.put(ME_URL, {"name": "Updated Name"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["data"]["name"] == "Updated Name"

    user.refresh_from_db()
    assert user.name == "Updated Name"


def test_profile_update_ignores_non_editable_fields(authenticated_client):
    client, user = authenticated_client
    original_phone = user.phone_number

    response = client.put(ME_URL, {"phone_number": "+910000000000", "role": "ADMIN"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.phone_number == original_phone
    assert user.role == "MEMBER"


def test_member_cannot_access_admin_only_permission(member_user):
    from core.permissions.roles import IsAdminRole

    class FakeRequest:
        user = member_user

    assert IsAdminRole().has_permission(FakeRequest(), None) is False
