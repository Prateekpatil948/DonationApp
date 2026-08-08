"""Abstract base models shared by every app.

Every concrete model in this project should inherit ``BaseModel`` (or
``SoftDeleteBaseModel`` when soft-delete is required) so it automatically
gets a UUID primary key, audit timestamps and, optionally, a soft-delete
flag - as mandated by the TRD's Database Design section.
"""

import uuid

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from apps.common.managers import SoftDeleteManager


class BaseModel(models.Model):
    """Abstract base providing a UUID PK plus created/updated audit fields."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteBaseModel(BaseModel):
    """``BaseModel`` extended with a soft-delete flag and a filtered manager."""

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta(BaseModel.Meta):
        abstract = True

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])
        return (1, {self._meta.label: 1})


class TempleSettings(BaseModel):
    """Singleton configuration for the temple: identity, receipt header/footer, numbering.

    Exactly one row should exist - enforced in the admin (``has_add_permission``)
    and via ``TempleSettingsService.get_settings()`` (get-or-create).
    """

    temple_name = models.CharField(max_length=255, default="")
    address = models.TextField(blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    logo_url = models.URLField(blank=True, default="")
    signature_url = models.URLField(blank=True, default="")
    registration_number = models.CharField(max_length=100, blank=True, default="")
    currency_symbol = models.CharField(max_length=5, default="₹")
    receipt_prefix = models.CharField(max_length=20, default="TDMS")
    last_receipt_number = models.PositiveIntegerField(default=0)

    class Meta(BaseModel.Meta):
        db_table = "temple_settings"
        verbose_name = "Temple Settings"
        verbose_name_plural = "Temple Settings"

    def __str__(self) -> str:
        return self.temple_name or "Temple Settings"


class AuditLog(models.Model):
    """Immutable trail of notable admin/service actions (invites, suspensions, edits, ...)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=100, db_index=True)
    target_type = models.CharField(max_length=100, blank=True, default="")
    target_id = models.CharField(max_length=64, blank=True, default="")
    details = models.JSONField(blank=True, default=dict, encoder=DjangoJSONEncoder)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["target_type", "target_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} @ {self.created_at:%Y-%m-%d %H:%M}"
