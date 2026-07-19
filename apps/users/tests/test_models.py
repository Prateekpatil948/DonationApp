import uuid

import pytest

pytestmark = pytest.mark.django_db


def test_user_has_uuid_primary_key(user_factory):
    user = user_factory()
    assert isinstance(user.id, uuid.UUID)


def test_user_full_name_property(user_factory):
    user = user_factory(first_name="Ada", last_name="Lovelace")
    assert user.full_name == "Ada Lovelace"


def test_user_str_returns_email(user_factory):
    user = user_factory(email="someone@example.com")
    assert str(user) == "someone@example.com"


def test_email_is_unique(user_factory):
    from django.db import IntegrityError

    user_factory(email="dup@example.com")
    with pytest.raises(IntegrityError):
        user_factory.build(email="dup@example.com").save(force_insert=True)
