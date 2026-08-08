"""Request/response serializers for the users app.

Explicit request/response serializers only, no ``fields = "__all__"`` - field
validation stays here, business logic stays in the service layer.
"""

from rest_framework import serializers

from apps.users.models import Invitation, User
from core.constants.choices import UserRole


class UserResponseSerializer(serializers.ModelSerializer):
    """Read-only representation of a user, returned by every user-facing endpoint."""

    class Meta:
        model = User
        fields = [
            "id",
            "phone_number",
            "name",
            "role",
            "status",
            "suspension_reason",
            "suspended_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class UserProfileUpdateRequestSerializer(serializers.Serializer):
    """Validates the editable subset of a profile: just the display name."""

    name = serializers.CharField(max_length=150, required=False, allow_blank=True)


class InviteMemberRequestSerializer(serializers.Serializer):
    """``POST /api/v1/members/invite`` request body."""

    phone_number = serializers.CharField(max_length=20)
    role = serializers.ChoiceField(choices=UserRole.choices, default=UserRole.MEMBER)

    def validate_phone_number(self, value: str) -> str:
        from core.validators.phone import validate_phone_number

        validate_phone_number(value)
        return value


class InvitationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ["id", "phone_number", "role", "status", "created_at", "accepted_at"]
        read_only_fields = fields


class MemberReasonRequestSerializer(serializers.Serializer):
    """Shared request body for suspend/reactivate/deactivate - a mandatory reason."""

    reason = serializers.CharField(max_length=255, allow_blank=False)
