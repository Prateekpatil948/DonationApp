import uuid

from django.db import IntegrityError

import pytest

pytestmark = pytest.mark.django_db


def test_user_has_uuid_primary_key(user_factory):
    user = user_factory()
    assert isinstance(user.id, uuid.UUID)


def test_user_str_includes_name_and_role(user_factory):
    user = user_factory(name="Ada Lovelace", role="MEMBER")
    assert str(user) == "Ada Lovelace (MEMBER)"


def test_phone_number_is_unique(user_factory):
    user_factory(phone_number="+919876500001")
    with pytest.raises(IntegrityError):
        user_factory.build(phone_number="+919876500001").save(force_insert=True)


def test_pin_is_hashed_not_stored_plaintext(user_factory):
    user = user_factory(pin="654321")
    assert user.password != "654321"
    assert user.check_password("654321") is True
