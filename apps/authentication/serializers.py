"""Request/response serializers for the authentication app."""

from rest_framework import serializers

from apps.users.serializers import UserResponseSerializer
from core.validators.phone import validate_phone_number

PIN_REGEX = r"^\d{6}$"


class SignupRequestSerializer(serializers.Serializer):
    """``POST /api/v1/auth/signup`` - complete signup for an invited phone number."""

    phone_number = serializers.CharField(max_length=20)
    pin = serializers.RegexField(
        PIN_REGEX, error_messages={"invalid": "PIN must be exactly 6 digits."}
    )
    confirm_pin = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=150)

    def validate_phone_number(self, value: str) -> str:
        validate_phone_number(value)
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs["pin"] != attrs["confirm_pin"]:
            raise serializers.ValidationError({"confirm_pin": "PIN and confirmation do not match."})
        return attrs


class LoginRequestSerializer(serializers.Serializer):
    """``POST /api/v1/auth/login`` - phone number + PIN login."""

    phone_number = serializers.CharField(max_length=20)
    pin = serializers.RegexField(
        PIN_REGEX, error_messages={"invalid": "PIN must be exactly 6 digits."}
    )

    def validate_phone_number(self, value: str) -> str:
        validate_phone_number(value)
        return value


class ChangePinRequestSerializer(serializers.Serializer):
    """``POST /api/v1/auth/change-pin`` - change the caller's own PIN."""

    old_pin = serializers.RegexField(PIN_REGEX)
    new_pin = serializers.RegexField(PIN_REGEX)


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
