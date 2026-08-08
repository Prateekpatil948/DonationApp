from django.core.management import call_command

import pytest

from apps.users.models import User

pytestmark = pytest.mark.django_db


def test_bootstrap_superuser_noop_without_env_vars(monkeypatch, capsys):
    monkeypatch.delenv("DJANGO_SUPERUSER_PHONE_NUMBER", raising=False)
    monkeypatch.delenv("DJANGO_SUPERUSER_PIN", raising=False)

    call_command("bootstrap_superuser")

    assert User.objects.count() == 0


def test_bootstrap_superuser_creates_admin(monkeypatch):
    monkeypatch.setenv("DJANGO_SUPERUSER_PHONE_NUMBER", "+919876545001")
    monkeypatch.setenv("DJANGO_SUPERUSER_PIN", "123456")
    monkeypatch.setenv("DJANGO_SUPERUSER_NAME", "Temple Admin")

    call_command("bootstrap_superuser")

    user = User.objects.get(phone_number="+919876545001")
    assert user.is_superuser is True
    assert user.name == "Temple Admin"


def test_bootstrap_superuser_is_idempotent(monkeypatch):
    monkeypatch.setenv("DJANGO_SUPERUSER_PHONE_NUMBER", "+919876545002")
    monkeypatch.setenv("DJANGO_SUPERUSER_PIN", "123456")

    call_command("bootstrap_superuser")
    call_command("bootstrap_superuser")

    assert User.objects.filter(phone_number="+919876545002").count() == 1
