"""Abstract base models shared by every app.

Every concrete model in this project should inherit ``BaseModel`` (or
``SoftDeleteBaseModel`` when soft-delete is required) so it automatically
gets a UUID primary key, audit timestamps and, optionally, a soft-delete
flag - as mandated by the TRD's Database Design section.
"""

import uuid

from django.conf import settings
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
