import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_owner_can_download_receipt_pdf(authenticated_client, donation_factory, temple_settings):
    client, user = authenticated_client
    donation = donation_factory(collected_by=user)

    response = client.get(f"/api/v1/receipts/{donation.id}/pdf")

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "application/pdf"


def test_other_member_cannot_download_receipt_pdf(
    authenticated_client, admin_user, donation_factory, temple_settings
):
    client, _ = authenticated_client
    other_donation = donation_factory(collected_by=admin_user)

    response = client.get(f"/api/v1/receipts/{other_donation.id}/pdf")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_receipt_json_detail(authenticated_client, donation_factory, temple_settings):
    client, user = authenticated_client
    donation = donation_factory(collected_by=user)

    response = client.get(f"/api/v1/receipts/{donation.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["receipt_number"] == donation.receipt_number
