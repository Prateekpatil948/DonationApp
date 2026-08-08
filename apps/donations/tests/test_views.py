import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

CATEGORIES_URL = "/api/v1/categories/"
DONATIONS_URL = "/api/v1/donations/"


def test_member_cannot_create_category(authenticated_client):
    client, _ = authenticated_client
    response = client.post(CATEGORIES_URL, {"name": "Hundi"}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_create_category(admin_client):
    client, _ = admin_client
    response = client.post(
        CATEGORIES_URL, {"name": "Hundi", "goal_amount": "5000.00"}, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["progress_percent"] == 0.0


def test_donation_requires_utr_for_upi(authenticated_client, category_factory, temple_settings):
    client, _ = authenticated_client
    category = category_factory()

    response = client.post(
        DONATIONS_URL,
        {
            "donor_name": "X",
            "category": str(category.id),
            "amount": "500.00",
            "payment_mode": "UPI",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "utr_number" in response.json()["error"]["details"]


def test_donation_create_and_fetch_own(authenticated_client, category_factory, temple_settings):
    client, user = authenticated_client
    category = category_factory()

    create_response = client.post(
        DONATIONS_URL,
        {
            "donor_name": "Suresh",
            "category": str(category.id),
            "amount": "250.00",
            "payment_mode": "CASH",
        },
        format="json",
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    donation_id = create_response.json()["data"]["id"]

    fetch_response = client.get(f"{DONATIONS_URL}{donation_id}/")
    assert fetch_response.status_code == status.HTTP_200_OK
    assert fetch_response.json()["data"]["collected_by"]["id"] == str(user.id)


def test_member_cannot_view_another_members_donation(
    authenticated_client, admin_user, donation_factory
):
    client, _ = authenticated_client
    other_donation = donation_factory(collected_by=admin_user)

    response = client.get(f"{DONATIONS_URL}{other_donation.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_category_list_filters_by_is_active(category_factory, authenticated_client):
    client, _ = authenticated_client
    category_factory(name="Active One", is_active=True)
    category_factory(name="Inactive One", is_active=False)

    response = client.get(f"{CATEGORIES_URL}?is_active=true")

    names = [row["name"] for row in response.json()["data"]]
    assert "Active One" in names
    assert "Inactive One" not in names


def test_admin_can_update_category(admin_client, category_factory):
    client, _ = admin_client
    category = category_factory(goal_amount="1000.00")

    response = client.patch(
        f"{CATEGORIES_URL}{category.id}/", {"goal_amount": "2000.00"}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["goal_amount"] == "2000.00"


def test_member_cannot_update_category(authenticated_client, category_factory):
    client, _ = authenticated_client
    category = category_factory()

    response = client.patch(
        f"{CATEGORIES_URL}{category.id}/", {"goal_amount": "1.00"}, format="json"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_donation_list_filters_by_category_and_payment_mode(
    authenticated_client, category_factory, donation_factory
):
    client, user = authenticated_client
    matching_category = category_factory()
    other_category = category_factory()
    matching = donation_factory(collected_by=user, category=matching_category, payment_mode="CASH")
    donation_factory(collected_by=user, category=other_category, payment_mode="CASH")
    donation_factory(
        collected_by=user, category=matching_category, payment_mode="UPI", utr_number="U1"
    )

    response = client.get(f"{DONATIONS_URL}?category={matching_category.id}&payment_mode=CASH")

    ids = [row["id"] for row in response.json()["data"]["results"]]
    assert ids == [str(matching.id)]


def test_donation_list_search_matches_donor_name(authenticated_client, donation_factory):
    client, user = authenticated_client
    donation_factory(collected_by=user, donor_name="Suresh Rao")
    donation_factory(collected_by=user, donor_name="Lakshmi")

    response = client.get(f"{DONATIONS_URL}?search=Suresh")

    results = response.json()["data"]["results"]
    assert len(results) == 1
    assert results[0]["donor_name"] == "Suresh Rao"


def test_admin_can_filter_donations_by_collected_by(admin_client, member_user, donation_factory):
    client, admin = admin_client
    member_donation = donation_factory(collected_by=member_user)
    donation_factory(collected_by=admin)

    response = client.get(f"{DONATIONS_URL}?collected_by={member_user.id}")

    ids = [row["id"] for row in response.json()["data"]["results"]]
    assert ids == [str(member_donation.id)]


def test_owner_can_update_donation(authenticated_client, donation_factory):
    client, user = authenticated_client
    donation = donation_factory(collected_by=user, amount="100.00")

    response = client.patch(f"{DONATIONS_URL}{donation.id}/", {"amount": "150.00"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["amount"] == "150.00"
