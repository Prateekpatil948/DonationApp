"""Aggregation queries backing the admin-facing report endpoints."""

from typing import Any

from django.db.models import Case, Count, DecimalField, QuerySet, Sum, When

from apps.donations.models import Donation
from core.constants.choices import PaymentMode
from services.base import BaseService


def _filtered_queryset(filters: dict[str, Any]) -> QuerySet[Donation]:
    queryset = Donation.objects.all()

    if category := filters.get("category"):
        queryset = queryset.filter(category_id=category)
    if member := filters.get("member"):
        queryset = queryset.filter(collected_by_id=member)
    if payment_mode := filters.get("payment_mode"):
        queryset = queryset.filter(payment_mode=payment_mode)
    if date_from := filters.get("date_from"):
        queryset = queryset.filter(donation_date__gte=date_from)
    if date_to := filters.get("date_to"):
        queryset = queryset.filter(donation_date__lte=date_to)

    return queryset


class ReportService(BaseService):
    """Read-only aggregation over ``Donation`` for the admin reports screens."""

    @staticmethod
    def summary(filters: dict[str, Any]) -> dict[str, Any]:
        queryset = _filtered_queryset(filters)
        aggregates = queryset.aggregate(
            total_collection=Sum("amount"),
            donation_count=Count("id"),
            cash_total=Sum(
                Case(
                    When(payment_mode=PaymentMode.CASH, then="amount"),
                    default=0,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            ),
            upi_total=Sum(
                Case(
                    When(payment_mode=PaymentMode.UPI, then="amount"),
                    default=0,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            ),
        )
        return {
            "total_collection": aggregates["total_collection"] or 0,
            "donation_count": aggregates["donation_count"] or 0,
            "cash_total": aggregates["cash_total"] or 0,
            "upi_total": aggregates["upi_total"] or 0,
        }

    @staticmethod
    def by_category(filters: dict[str, Any]) -> list[dict[str, Any]]:
        queryset = _filtered_queryset(filters)
        rows = (
            queryset.values("category_id", "category__name", "category__goal_amount")
            .annotate(collected_amount=Sum("amount"), donation_count=Count("id"))
            .order_by("category__sort_order", "category__name")
        )

        results = []
        for row in rows:
            goal = row["category__goal_amount"]
            collected = row["collected_amount"] or 0
            progress = round(float(collected) / float(goal) * 100, 2) if goal else None
            results.append(
                {
                    "category_id": row["category_id"],
                    "category_name": row["category__name"],
                    "goal_amount": goal,
                    "collected_amount": collected,
                    "donation_count": row["donation_count"],
                    "progress_percent": progress,
                }
            )
        return results

    @staticmethod
    def by_member(filters: dict[str, Any]) -> list[dict[str, Any]]:
        queryset = _filtered_queryset(filters)
        rows = (
            queryset.values("collected_by_id", "collected_by__name", "collected_by__phone_number")
            .annotate(total_collected=Sum("amount"), donation_count=Count("id"))
            .order_by("-total_collected")
        )
        return [
            {
                "member_id": row["collected_by_id"],
                "member_name": row["collected_by__name"],
                "phone_number": row["collected_by__phone_number"],
                "total_collected": row["total_collected"] or 0,
                "donation_count": row["donation_count"],
            }
            for row in rows
        ]

    @staticmethod
    def by_date(filters: dict[str, Any]) -> list[dict[str, Any]]:
        queryset = _filtered_queryset(filters)
        rows = (
            queryset.values("donation_date")
            .annotate(
                total_collected=Sum("amount"),
                donation_count=Count("id"),
                cash_total=Sum(
                    Case(
                        When(payment_mode=PaymentMode.CASH, then="amount"),
                        default=0,
                        output_field=DecimalField(max_digits=12, decimal_places=2),
                    )
                ),
                upi_total=Sum(
                    Case(
                        When(payment_mode=PaymentMode.UPI, then="amount"),
                        default=0,
                        output_field=DecimalField(max_digits=12, decimal_places=2),
                    )
                ),
            )
            .order_by("donation_date")
        )
        return [
            {
                "date": row["donation_date"],
                "total_collected": row["total_collected"] or 0,
                "donation_count": row["donation_count"],
                "cash_total": row["cash_total"] or 0,
                "upi_total": row["upi_total"] or 0,
            }
            for row in rows
        ]
