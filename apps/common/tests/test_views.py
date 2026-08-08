import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

TEMPLE_SETTINGS_URL = "/api/v1/temple-settings/"


def test_active_member_can_read_temple_settings(authenticated_client, temple_settings):
    client, _ = authenticated_client
    response = client.get(TEMPLE_SETTINGS_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["temple_name"] == temple_settings.temple_name


def test_member_cannot_update_temple_settings(authenticated_client, temple_settings):
    client, _ = authenticated_client
    response = client.put(TEMPLE_SETTINGS_URL, {"temple_name": "New Name"}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_update_temple_settings(admin_client, temple_settings):
    client, _ = admin_client
    response = client.put(TEMPLE_SETTINGS_URL, {"temple_name": "New Temple Name"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["temple_name"] == "New Temple Name"
