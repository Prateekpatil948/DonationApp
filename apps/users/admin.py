from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.users.models import Invitation, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["-created_at"]
    list_display = ["phone_number", "name", "role", "status", "is_staff"]
    list_filter = ["role", "status", "is_staff"]
    search_fields = ["phone_number", "name"]
    readonly_fields = ["id", "created_at", "updated_at", "last_login"]
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal info", {"fields": ("name",)}),
        (
            "Role & status",
            {
                "fields": (
                    "role",
                    "status",
                    "suspension_reason",
                    "suspended_at",
                    "suspended_by",
                    "invited_by",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "role", "status", "password1", "password2"),
            },
        ),
    )


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ["phone_number", "role", "status", "invited_by", "created_at", "accepted_at"]
    list_filter = ["status", "role"]
    search_fields = ["phone_number"]
    readonly_fields = ["id", "created_at", "accepted_at"]
