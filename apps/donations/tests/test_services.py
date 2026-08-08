from decimal import Decimal

import pytest

from apps.donations.services import CategoryService, DonationService

pytestmark = pytest.mark.django_db


def test_create_donation_generates_sequential_receipt_numbers(
    temple_settings, category_factory, member_user
):
    category = category_factory()

    first = DonationService.create(
        member_user,
        {
            "donor_name": "Suresh",
            "category": category,
            "amount": Decimal("100.00"),
            "payment_mode": "CASH",
        },
    )
    second = DonationService.create(
        member_user,
        {
            "donor_name": "Lakshmi",
            "category": category,
            "amount": Decimal("200.00"),
            "payment_mode": "CASH",
        },
    )

    assert first.receipt_number == f"{temple_settings.receipt_prefix}-000001"
    assert second.receipt_number == f"{temple_settings.receipt_prefix}-000002"


def test_donation_list_scopes_members_to_their_own_entries(
    admin_user, member_user, donation_factory
):
    own = donation_factory(collected_by=member_user)
    donation_factory(collected_by=admin_user)

    results = DonationService.list(member_user, {})

    assert list(results) == [own]


def test_donation_list_shows_admin_everything(admin_user, member_user, donation_factory):
    donation_factory(collected_by=member_user)
    donation_factory(collected_by=admin_user)

    results = DonationService.list(admin_user, {})

    assert results.count() == 2


def test_category_collected_amount_sums_donations(category_factory, donation_factory):
    category = category_factory(goal_amount="1000.00")
    donation_factory(category=category, amount="300.00")
    donation_factory(category=category, amount="150.50")

    assert CategoryService.collected_amount(category) == Decimal("450.50")
