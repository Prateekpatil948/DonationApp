import pytest

from apps.users.serializers import UserProfileUpdateRequestSerializer, UserResponseSerializer

pytestmark = pytest.mark.django_db


def test_user_response_serializer_exposes_expected_fields(user_factory):
    user = user_factory()
    data = UserResponseSerializer(user).data

    assert set(data.keys()) == {
        "id",
        "phone_number",
        "name",
        "role",
        "status",
        "suspension_reason",
        "suspended_at",
        "created_at",
        "updated_at",
    }


def test_profile_update_serializer_accepts_name_only():
    serializer = UserProfileUpdateRequestSerializer(data={"name": "New Name"})
    assert serializer.is_valid()
    assert serializer.validated_data == {"name": "New Name"}


def test_profile_update_serializer_has_no_phone_or_role_field():
    serializer = UserProfileUpdateRequestSerializer(data={})
    assert "phone_number" not in serializer.fields
    assert "role" not in serializer.fields
    assert "status" not in serializer.fields
