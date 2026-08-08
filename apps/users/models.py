"""Custom user model: phone number + PIN accounts with an Admin/Member role."""

import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.users.managers import UserManager
from core.constants.choices import InvitationStatus, MemberStatus, UserRole
from core.validators.phone import validate_phone_number


class User(AbstractBaseUser, PermissionsMixin):
    """Application user: a temple admin or a member who collects donations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, unique=True, validators=[validate_phone_number])
    name = models.CharField(max_length=150, blank=True, default="")
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.MEMBER)
    status = models.CharField(
        max_length=20, choices=MemberStatus.choices, default=MemberStatus.PENDING
    )

    invited_by = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="invited_users"
    )
    suspension_reason = models.CharField(max_length=255, blank=True, default="")
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspended_by = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["role"]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone_number"]),
            models.Index(fields=["role"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.name or self.phone_number} ({self.role})"


class Invitation(models.Model):
    """Audit-friendly record of an admin inviting a phone number to join."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, validators=[validate_phone_number])
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.MEMBER)
    invited_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="sent_invitations"
    )
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE, related_name="invitations"
    )
    status = models.CharField(
        max_length=20, choices=InvitationStatus.choices, default=InvitationStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "invitations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone_number"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"Invitation({self.phone_number}, {self.status})"
