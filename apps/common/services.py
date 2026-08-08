"""Cross-cutting business logic shared by every app: audit trail + temple config."""

from typing import Any

from django.db import models as django_models

from apps.common.models import AuditLog, TempleSettings
from apps.users.models import User
from services.base import BaseService


class AuditService(BaseService):
    """Writes an immutable ``AuditLog`` row for a notable action."""

    @staticmethod
    def log(
        actor: User | None,
        action: str,
        target: django_models.Model | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        return AuditLog.objects.create(
            actor=actor,
            action=action,
            target_type=target._meta.label if target is not None else "",
            target_id=str(target.pk) if target is not None else "",
            details=details or {},
        )


class TempleSettingsService(BaseService):
    """Manages the single ``TempleSettings`` row."""

    @staticmethod
    def get_settings() -> TempleSettings:
        settings_row = TempleSettings.objects.first()
        if settings_row is None:
            settings_row = TempleSettings.objects.create(temple_name="Temple")
        return settings_row

    @classmethod
    def update_settings(cls, validated_data: dict[str, Any]) -> TempleSettings:
        settings_row = cls.get_settings()
        for field, value in validated_data.items():
            setattr(settings_row, field, value)
        settings_row.save(update_fields=list(validated_data.keys()))
        return settings_row
