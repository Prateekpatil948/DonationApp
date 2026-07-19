"""Request/response serializers for the users app.

Per the TRD's Serializer Guidelines: every endpoint gets an explicit request
serializer and response serializer, no ``fields = "__all__"``, and field-level
validation stays here while business logic stays in the service layer.
"""

from rest_framework import serializers

from apps.users.models import User
from core.validators.phone import validate_phone_number


class UserResponseSerializer(serializers.ModelSerializer):
    """Read-only representation of a user, returned by every user-facing endpoint."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "profile_picture",
            "phone_number",
            "user_type",
            "is_active",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class UserProfileUpdateRequestSerializer(serializers.Serializer):
    """Validates the editable subset of a profile: name, phone, profile photo.

    Email, ``google_id`` and ``user_type`` are intentionally absent - the TRD
    marks them as not editable via ``PUT /users/me``.
    """

    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    profile_picture = serializers.URLField(max_length=200, required=False, allow_blank=True)

    def validate_phone_number(self, value: str) -> str:
        validate_phone_number(value)
        return value
