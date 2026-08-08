import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_member_cannot_access_reports(authenticated_client):
    client, _ = authenticated_client
    response = client.get("/api/v1/reports/summary")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_fetch_summary_report(admin_client, donation_factory):
    client, _ = admin_client
    donation_factory(amount="100.00")

    response = client.get("/api/v1/reports/summary")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["donation_count"] == 1


def test_admin_can_export_csv(admin_client, donation_factory):
    client, _ = admin_client
    donation_factory(amount="100.00")

    response = client.get("/api/v1/reports/category?export=csv")

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "text/csv"


def test_admin_can_export_excel(admin_client, donation_factory):
    client, _ = admin_client
    donation_factory(amount="100.00")

    response = client.get("/api/v1/reports/category?export=excel")

    assert response.status_code == status.HTTP_200_OK
    assert "spreadsheetml" in response["Content-Type"]


def test_admin_can_export_pdf(admin_client, donation_factory):
    client, _ = admin_client
    donation_factory(amount="100.00")

    response = client.get("/api/v1/reports/category?export=pdf")

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_member_and_date_reports(admin_client, donation_factory):
    client, _ = admin_client
    donation_factory(amount="100.00")

    member_response = client.get("/api/v1/reports/member")
    date_response = client.get("/api/v1/reports/date")

    assert member_response.status_code == status.HTTP_200_OK
    assert date_response.status_code == status.HTTP_200_OK
    assert len(member_response.json()["data"]) == 1
    assert len(date_response.json()["data"]) == 1
