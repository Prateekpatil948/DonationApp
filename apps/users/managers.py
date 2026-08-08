"""Custom manager for the ``User`` model (phone number + PIN, no username)."""

from typing import TYPE_CHECKING, Any

from django.contrib.auth.base_user import BaseUserManager

if TYPE_CHECKING:
    from apps.users.models import User


class UserManager(BaseUserManager["User"]):
    use_in_migrations = True

    def _create_user(
        self, phone_number: str, pin: str | None = None, **extra_fields: Any
    ) -> "User":
        if not phone_number:
            raise ValueError("Users must have a phone number.")
        user = self.model(phone_number=phone_number, **extra_fields)
        if pin:
            user.set_password(pin)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, phone_number: str, pin: str | None = None, **extra_fields: Any) -> "User":
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, pin, **extra_fields)

    def create_superuser(
        self, phone_number: str, pin: str | None = None, **extra_fields: Any
    ) -> "User":
        from core.constants.choices import MemberStatus, UserRole

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("status", MemberStatus.ACTIVE)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, pin, **extra_fields)
