"""Request/response serializers for the common app (temple settings)."""

from rest_framework import serializers

from apps.common.models import TempleSettings


class TempleSettingsResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempleSettings
        fields = [
            "id",
            "temple_name",
            "address",
            "phone",
            "email",
            "logo_url",
            "signature_url",
            "registration_number",
            "currency_symbol",
            "receipt_prefix",
        ]
        read_only_fields = fields


class TempleSettingsUpdateRequestSerializer(serializers.Serializer):
    """``PUT /api/v1/temple-settings/`` request body (admin only)."""

    temple_name = serializers.CharField(max_length=255, required=False)
    address = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    logo_url = serializers.URLField(required=False, allow_blank=True)
    signature_url = serializers.URLField(required=False, allow_blank=True)
    registration_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    currency_symbol = serializers.CharField(max_length=5, required=False)
    receipt_prefix = serializers.CharField(max_length=20, required=False)
