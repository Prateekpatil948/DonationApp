import pytest

from apps.users.models import User
from core.constants.choices import UserRole

pytestmark = pytest.mark.django_db


def test_create_user_hashes_pin():
    user = User.objects.create_user(
        phone_number="+919876544001", pin="123456", role=UserRole.MEMBER
    )
    assert user.is_staff is False
    assert user.check_password("123456") is True


def test_create_user_without_pin_is_unusable():
    user = User.objects.create_user(phone_number="+919876544002")
    assert user.has_usable_password() is False


def test_create_superuser_sets_admin_role_and_flags():
    user = User.objects.create_superuser(phone_number="+919876544003", pin="123456")
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.role == UserRole.ADMIN


def test_create_superuser_rejects_is_staff_false():
    with pytest.raises(ValueError):
        User.objects.create_superuser(phone_number="+919876544004", pin="123456", is_staff=False)
