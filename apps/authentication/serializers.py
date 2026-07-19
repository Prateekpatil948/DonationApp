"""Request/response serializers for the authentication app."""

from rest_framework import serializers

from apps.users.serializers import UserResponseSerializer
from core.constants.choices import UserType
from core.validators.phone import validate_phone_number


class GoogleLoginRequestSerializer(serializers.Serializer):
    """``POST /api/v1/auth/google/login`` request body.

    All three fields are mandatory per the TRD's Validation Rules -
    ``phone_number``/``user_type`` are required even on repeat logins since
    the same endpoint handles both sign-up and sign-in.
    """

    id_token = serializers.CharField(allow_blank=False)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    user_type = serializers.ChoiceField(choices=UserType.choices)

    def validate_phone_number(self, value: str) -> str:
        validate_phone_number(value)
        return value


class TokenPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserResponseSerializer()


class LogoutRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class TokenRefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField(required=False)
