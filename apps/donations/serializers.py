"""Request/response serializers for the donations app."""

from decimal import Decimal

from rest_framework import serializers

from apps.donations.models import Donation, DonationCategory
from apps.donations.services import CategoryService
from apps.users.serializers import UserResponseSerializer
from core.constants.choices import PaymentMode
from core.validators.phone import validate_phone_number


class CategoryResponseSerializer(serializers.ModelSerializer):
    collected_amount = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = DonationCategory
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "goal_amount",
            "color",
            "sort_order",
            "collected_amount",
            "progress_percent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_collected_amount(self, obj: DonationCategory) -> Decimal:
        return CategoryService.collected_amount(obj)

    def get_progress_percent(self, obj: DonationCategory) -> float | None:
        if not obj.goal_amount:
            return None
        collected = CategoryService.collected_amount(obj)
        return round(float(collected) / float(obj.goal_amount) * 100, 2)


class CategoryWriteRequestSerializer(serializers.Serializer):
    """Shared create/update body for ``DonationCategory`` (admin only)."""

    name = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)
    goal_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, allow_null=True, min_value=Decimal("0")
    )
    color = serializers.CharField(max_length=7, required=False)
    sort_order = serializers.IntegerField(required=False)


class DonationResponseSerializer(serializers.ModelSerializer):
    category = CategoryResponseSerializer(read_only=True)
    collected_by = UserResponseSerializer(read_only=True)

    class Meta:
        model = Donation
        fields = [
            "id",
            "receipt_number",
            "donation_date",
            "donor_name",
            "donor_phone",
            "donor_address",
            "category",
            "amount",
            "payment_mode",
            "utr_number",
            "remarks",
            "receipt_language",
            "collected_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class DonationCreateRequestSerializer(serializers.Serializer):
    """``POST /api/v1/donations/`` request body."""

    donation_date = serializers.DateField(required=False)
    donor_name = serializers.CharField(max_length=150)
    donor_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    donor_address = serializers.CharField(required=False, allow_blank=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=DonationCategory.objects.filter(is_active=True)
    )
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    payment_mode = serializers.ChoiceField(choices=PaymentMode.choices)
    utr_number = serializers.CharField(max_length=64, required=False, allow_blank=True)
    remarks = serializers.CharField(required=False, allow_blank=True)
    receipt_language = serializers.CharField(max_length=5, required=False)

    def validate_donor_phone(self, value: str) -> str:
        validate_phone_number(value)
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs.get("payment_mode") == PaymentMode.UPI and not attrs.get("utr_number"):
            raise serializers.ValidationError(
                {"utr_number": "UTR number is required for UPI payments."}
            )
        return attrs


class DonationUpdateRequestSerializer(serializers.Serializer):
    """``PUT/PATCH /api/v1/donations/{id}/`` request body - same fields, all optional."""

    donation_date = serializers.DateField(required=False)
    donor_name = serializers.CharField(max_length=150, required=False)
    donor_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    donor_address = serializers.CharField(required=False, allow_blank=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=DonationCategory.objects.filter(is_active=True), required=False
    )
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01"), required=False
    )
    payment_mode = serializers.ChoiceField(choices=PaymentMode.choices, required=False)
    utr_number = serializers.CharField(max_length=64, required=False, allow_blank=True)
    remarks = serializers.CharField(required=False, allow_blank=True)
    receipt_language = serializers.CharField(max_length=5, required=False)

    def validate_donor_phone(self, value: str) -> str:
        validate_phone_number(value)
        return value
