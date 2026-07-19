import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_health_check_returns_200_when_healthy(api_client):
    response = api_client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["database"] == "up"
    assert body["application"] == "up"
    assert "version" in body
    assert "uptime_seconds" in body
