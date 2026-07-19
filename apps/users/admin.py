from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.users.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["-created_at"]
    list_display = [
        "email",
        "first_name",
        "last_name",
        "user_type",
        "is_active",
        "is_verified",
        "is_staff",
    ]
    list_filter = ["user_type", "is_active", "is_verified", "is_staff"]
    search_fields = ["email", "first_name", "last_name", "phone_number"]
    readonly_fields = ["id", "google_id", "created_at", "updated_at", "last_login"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "phone_number", "profile_picture")},
        ),
        (
            "Role & status",
            {
                "fields": (
                    "user_type",
                    "is_active",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Google", {"fields": ("google_id",)}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "phone_number", "user_type", "password1", "password2"),
            },
        ),
    )
