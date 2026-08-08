from django.contrib import admin
from django.http import HttpRequest

from apps.common.models import AuditLog, TempleSettings


@admin.register(TempleSettings)
class TempleSettingsAdmin(admin.ModelAdmin):
    list_display = ["temple_name", "receipt_prefix", "last_receipt_number"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return not TempleSettings.objects.exists()


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["action", "actor", "target_type", "target_id", "created_at"]
    list_filter = ["action", "target_type"]
    search_fields = ["action", "target_type", "target_id"]
    readonly_fields = ["id", "actor", "action", "target_type", "target_id", "details", "created_at"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: AuditLog | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: AuditLog | None = None) -> bool:
        return False
