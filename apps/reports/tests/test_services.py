from decimal import Decimal

import pytest

from apps.reports.services import ReportService

pytestmark = pytest.mark.django_db


def test_summary_aggregates_cash_and_upi_totals(donation_factory):
    donation_factory(amount="100.00", payment_mode="CASH")
    donation_factory(amount="250.00", payment_mode="UPI", utr_number="UTR1")

    summary = ReportService.summary({})

    assert summary["total_collection"] == Decimal("350.00")
    assert summary["cash_total"] == Decimal("100.00")
    assert summary["upi_total"] == Decimal("250.00")
    assert summary["donation_count"] == 2


def test_by_category_includes_goal_progress(category_factory, donation_factory):
    category = category_factory(goal_amount="1000.00")
    donation_factory(category=category, amount="250.00")

    rows = ReportService.by_category({})

    assert rows[0]["progress_percent"] == 25.0


def test_by_member_groups_by_collected_by(member_user, donation_factory):
    donation_factory(collected_by=member_user, amount="100.00")
    donation_factory(collected_by=member_user, amount="50.00")

    rows = ReportService.by_member({})

    assert rows[0]["total_collected"] == Decimal("150.00")
    assert rows[0]["donation_count"] == 2


def test_by_date_filters_by_date_range(donation_factory):
    donation_factory(donation_date="2026-01-01", amount="10.00")
    donation_factory(donation_date="2026-06-01", amount="20.00")

    rows = ReportService.by_date({"date_from": "2026-05-01", "date_to": "2026-12-31"})

    assert len(rows) == 1
    assert str(rows[0]["date"]) == "2026-06-01"
