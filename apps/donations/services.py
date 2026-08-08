"""Business logic for donation categories and donation entries."""

from datetime import date
from typing import Any

from django.db import transaction
from django.db.models import Q, QuerySet, Sum

from apps.common.models import TempleSettings
from apps.common.services import AuditService
from apps.donations.models import Donation, DonationCategory
from apps.users.models import User
from core.constants.choices import UserRole
from services.base import BaseService


class CategoryService(BaseService):
    """CRUD for ``DonationCategory``, including goal-progress reads."""

    @staticmethod
    def list(filters: dict[str, Any]) -> QuerySet[DonationCategory]:
        queryset = DonationCategory.objects.all()
        if (is_active := filters.get("is_active")) is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset

    @staticmethod
    def get_by_id(category_id: str) -> DonationCategory:
        return DonationCategory.objects.get(id=category_id)

    @classmethod
    def create(cls, actor: User, validated_data: dict[str, Any]) -> DonationCategory:
        with transaction.atomic():
            category = DonationCategory.objects.create(
                **validated_data, created_by=actor, updated_by=actor
            )
        AuditService.log(actor, "CATEGORY_CREATED", target=category, details=validated_data)
        return category

    @classmethod
    def update(
        cls, actor: User, category: DonationCategory, validated_data: dict[str, Any]
    ) -> DonationCategory:
        with transaction.atomic():
            for field, value in validated_data.items():
                setattr(category, field, value)
            category.updated_by = actor
            category.save(update_fields=[*validated_data.keys(), "updated_by"])
        AuditService.log(actor, "CATEGORY_UPDATED", target=category, details=validated_data)
        return category

    @staticmethod
    def collected_amount(category: DonationCategory) -> Any:
        return category.donations.aggregate(total=Sum("amount"))["total"] or 0


class DonationService(BaseService):
    """CRUD for ``Donation``, including atomic receipt-number generation."""

    @staticmethod
    def list(user: User, filters: dict[str, Any]) -> QuerySet[Donation]:
        queryset = Donation.objects.select_related("category", "collected_by")

        if user.role != UserRole.ADMIN:
            queryset = queryset.filter(collected_by=user)
        elif collected_by := filters.get("collected_by"):
            queryset = queryset.filter(collected_by_id=collected_by)

        if category := filters.get("category"):
            queryset = queryset.filter(category_id=category)
        if payment_mode := filters.get("payment_mode"):
            queryset = queryset.filter(payment_mode=payment_mode)
        if date_from := filters.get("date_from"):
            queryset = queryset.filter(donation_date__gte=date_from)
        if date_to := filters.get("date_to"):
            queryset = queryset.filter(donation_date__lte=date_to)
        if search := filters.get("search"):
            queryset = queryset.filter(
                Q(donor_name__icontains=search)
                | Q(donor_phone__icontains=search)
                | Q(receipt_number__icontains=search)
            )

        return queryset

    @staticmethod
    def get_by_id(donation_id: str) -> Donation:
        return Donation.objects.select_related("category", "collected_by").get(id=donation_id)

    @staticmethod
    def _next_receipt_number() -> str:
        settings_row = TempleSettings.objects.select_for_update().first()
        if settings_row is None:
            settings_row = TempleSettings.objects.create(temple_name="Temple")
            settings_row = TempleSettings.objects.select_for_update().get(pk=settings_row.pk)

        settings_row.last_receipt_number += 1
        settings_row.save(update_fields=["last_receipt_number"])
        return f"{settings_row.receipt_prefix}-{settings_row.last_receipt_number:06d}"

    @classmethod
    def create(cls, collected_by: User, validated_data: dict[str, Any]) -> Donation:
        validated_data.setdefault("donation_date", date.today())
        with transaction.atomic():
            receipt_number = cls._next_receipt_number()
            donation = Donation.objects.create(
                **validated_data,
                collected_by=collected_by,
                receipt_number=receipt_number,
                created_by=collected_by,
                updated_by=collected_by,
            )
        return donation

    @classmethod
    def update(cls, actor: User, donation: Donation, validated_data: dict[str, Any]) -> Donation:
        with transaction.atomic():
            for field, value in validated_data.items():
                setattr(donation, field, value)
            donation.updated_by = actor
            donation.save(update_fields=[*validated_data.keys(), "updated_by"])
        AuditService.log(actor, "DONATION_EDITED", target=donation, details=validated_data)
        return donation
