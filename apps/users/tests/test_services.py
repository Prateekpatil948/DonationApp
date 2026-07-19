import pytest

from apps.users.services import UserService

pytestmark = pytest.mark.django_db


def test_create_from_google_profile_persists_user():
    user = UserService.create_from_google_profile(
        email="new@example.com",
        google_id="gid-1",
        first_name="Ada",
        last_name="Lovelace",
        profile_picture="https://example.com/p.jpg",
        phone_number="+919876543210",
        user_type="ANALYST",
    )

    assert user.pk is not None
    assert user.is_verified is True


def test_get_by_google_id_returns_none_when_missing():
    assert UserService.get_by_google_id("does-not-exist") is None


def test_update_profile_only_touches_editable_fields(user_factory):
    user = user_factory(first_name="Old")
    original_email = user.email

    updated = UserService.update_profile(user, {"first_name": "New"})

    assert updated.first_name == "New"
    assert updated.email == original_email
