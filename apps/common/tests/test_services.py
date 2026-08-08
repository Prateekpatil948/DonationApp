import pytest

from apps.common.models import AuditLog, TempleSettings
from apps.common.services import AuditService, TempleSettingsService

pytestmark = pytest.mark.django_db


def test_get_settings_creates_a_default_row_when_none_exists():
    assert TempleSettings.objects.count() == 0

    settings_row = TempleSettingsService.get_settings()

    assert TempleSettings.objects.count() == 1
    assert settings_row.temple_name


def test_get_settings_is_idempotent():
    first = TempleSettingsService.get_settings()
    second = TempleSettingsService.get_settings()
    assert first.pk == second.pk


def test_update_settings_persists_changes():
    TempleSettingsService.get_settings()
    updated = TempleSettingsService.update_settings({"temple_name": "Sri Venkateshwara Temple"})
    assert updated.temple_name == "Sri Venkateshwara Temple"


def test_audit_log_serializes_decimal_details(admin_user, category_factory):
    category = category_factory()

    log = AuditService.log(
        admin_user,
        "CATEGORY_CREATED",
        target=category,
        details={"goal_amount": category.goal_amount},
    )

    assert AuditLog.objects.filter(pk=log.pk).exists()
    log.refresh_from_db()
    assert log.details["goal_amount"] == str(category.goal_amount)
