"""Business logic for the users app: profile, invitations and member lifecycle."""

from typing import Any

from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

from apps.common.services import AuditService
from apps.users.models import Invitation, User
from core.constants.choices import InvitationStatus, MemberStatus
from core.exceptions.exceptions import DuplicateInvitationError
from services.base import BaseService

EDITABLE_PROFILE_FIELDS = ("name",)


class UserService(BaseService):
    """Encapsulates all read/write operations on ``User``."""

    @staticmethod
    def get_by_id(user_id: str) -> User:
        return User.objects.get(id=user_id)

    @staticmethod
    def get_by_phone_number(phone_number: str) -> User | None:
        return User.objects.filter(phone_number=phone_number).first()

    @classmethod
    def update_profile(cls, user: User, validated_data: dict[str, Any]) -> User:
        fields_to_update = []
        for field in EDITABLE_PROFILE_FIELDS:
            if field in validated_data:
                setattr(user, field, validated_data[field])
                fields_to_update.append(field)

        if fields_to_update:
            with transaction.atomic():
                user.save(update_fields=fields_to_update)
        return user

    @staticmethod
    def list_members(filters: dict[str, Any]) -> QuerySet[User]:
        queryset = User.objects.all()

        if status := filters.get("status"):
            queryset = queryset.filter(status=status)
        if role := filters.get("role"):
            queryset = queryset.filter(role=role)
        if search := filters.get("search"):
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(phone_number__icontains=search)
            )

        return queryset

    @staticmethod
    def suspend(actor: User, user: User, reason: str) -> User:
        with transaction.atomic():
            user.status = MemberStatus.SUSPENDED
            user.is_active = False
            user.suspension_reason = reason
            user.suspended_at = timezone.now()
            user.suspended_by = actor
            user.save(
                update_fields=[
                    "status",
                    "is_active",
                    "suspension_reason",
                    "suspended_at",
                    "suspended_by",
                ]
            )
        AuditService.log(actor, "MEMBER_SUSPENDED", target=user, details={"reason": reason})
        return user

    @staticmethod
    def reactivate(actor: User, user: User, reason: str) -> User:
        with transaction.atomic():
            user.status = MemberStatus.ACTIVE
            user.is_active = True
            user.suspension_reason = ""
            user.suspended_at = None
            user.suspended_by = None
            user.save(
                update_fields=[
                    "status",
                    "is_active",
                    "suspension_reason",
                    "suspended_at",
                    "suspended_by",
                ]
            )
        AuditService.log(actor, "MEMBER_REACTIVATED", target=user, details={"reason": reason})
        return user

    @staticmethod
    def deactivate(actor: User, user: User, reason: str) -> User:
        with transaction.atomic():
            user.status = MemberStatus.INACTIVE
            user.is_active = False
            user.suspension_reason = reason
            user.save(update_fields=["status", "is_active", "suspension_reason"])
        AuditService.log(actor, "MEMBER_DEACTIVATED", target=user, details={"reason": reason})
        return user


class InvitationService(BaseService):
    """Handles inviting new phone numbers to join as members or admins."""

    @classmethod
    def invite(cls, actor: User, phone_number: str, role: str) -> Invitation:
        existing = User.objects.filter(phone_number=phone_number).first()
        if existing is not None and existing.status != MemberStatus.PENDING:
            raise DuplicateInvitationError()
        if existing is not None and existing.status == MemberStatus.PENDING:
            has_open_invite = Invitation.objects.filter(
                phone_number=phone_number, status=InvitationStatus.PENDING
            ).exists()
            if has_open_invite:
                raise DuplicateInvitationError()

        with transaction.atomic():
            user = existing or User.objects.create_user(
                phone_number=phone_number,
                role=role,
                status=MemberStatus.PENDING,
                invited_by=actor,
                is_active=False,
            )
            invitation = Invitation.objects.create(
                phone_number=phone_number, role=role, invited_by=actor, user=user
            )

        AuditService.log(actor, "MEMBER_INVITED", target=user, details={"role": role})
        return invitation
