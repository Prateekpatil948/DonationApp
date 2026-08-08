import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

INVITE_URL = "/api/v1/members/invite"
LIST_URL = "/api/v1/members/"


def test_member_cannot_invite(authenticated_client):
    client, _ = authenticated_client
    response = client.post(INVITE_URL, {"phone_number": "+919876511111"}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_invite_a_member(admin_client):
    client, _ = admin_client
    response = client.post(
        INVITE_URL, {"phone_number": "+919876511112", "role": "MEMBER"}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["status"] == "PENDING"


def test_admin_can_list_members(admin_client, member_user):
    client, _ = admin_client
    response = client.get(LIST_URL)
    assert response.status_code == status.HTTP_200_OK
    phone_numbers = [row["phone_number"] for row in response.json()["data"]["results"]]
    assert member_user.phone_number in phone_numbers


def test_suspend_requires_a_reason(admin_client, member_user):
    client, _ = admin_client
    response = client.post(f"/api/v1/members/{member_user.id}/suspend", {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_suspend_then_reactivate(admin_client, member_user):
    client, _ = admin_client

    suspend_response = client.post(
        f"/api/v1/members/{member_user.id}/suspend", {"reason": "test"}, format="json"
    )
    assert suspend_response.status_code == status.HTTP_200_OK
    assert suspend_response.json()["data"]["status"] == "SUSPENDED"

    reactivate_response = client.post(
        f"/api/v1/members/{member_user.id}/reactivate", {"reason": "resolved"}, format="json"
    )
    assert reactivate_response.status_code == status.HTTP_200_OK
    assert reactivate_response.json()["data"]["status"] == "ACTIVE"
