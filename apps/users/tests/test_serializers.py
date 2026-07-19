import pytest

from apps.users.serializers import UserProfileUpdateRequestSerializer, UserResponseSerializer

pytestmark = pytest.mark.django_db


def test_user_response_serializer_exposes_expected_fields(user_factory):
    user = user_factory()
    data = UserResponseSerializer(user).data

    assert set(data.keys()) == {
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
    }


def test_profile_update_serializer_accepts_valid_phone():
    serializer = UserProfileUpdateRequestSerializer(data={"phone_number": "+919876543210"})
    assert serializer.is_valid()


def test_profile_update_serializer_rejects_invalid_phone():
    serializer = UserProfileUpdateRequestSerializer(data={"phone_number": "abc"})
    assert not serializer.is_valid()
    assert "phone_number" in serializer.errors


def test_profile_update_serializer_has_no_email_or_user_type_field():
    serializer = UserProfileUpdateRequestSerializer(data={})
    assert "email" not in serializer.fields
    assert "google_id" not in serializer.fields
    assert "user_type" not in serializer.fields
