"""Business logic for the authentication app.

``TokenService`` issues and manages JWTs; ``AuthenticationService`` orchestrates
signup (PIN set-up for an invited phone number), login (phone + PIN, like a
UPI MPIN) and PIN changes, so views stay a thin authenticate/validate/invoke/
respond layer.
"""

import logging
from typing import Any

from django.db import transaction
from django.utils import timezone

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import Invitation, User
from apps.users.services import UserService
from core.constants.choices import InvitationStatus, MemberStatus
from core.exceptions.exceptions import (
    AccountInactiveError,
    AccountPendingError,
    AccountSuspendedError,
    AlreadyRegisteredError,
    InvalidCredentialsError,
    NotInvitedError,
    ServiceError,
)
from services.base import BaseService

logger = logging.getLogger(__name__)


class TokenService(BaseService):
    """Issues, refreshes and revokes JWT access/refresh token pairs."""

    @staticmethod
    def issue_tokens_for_user(user: User) -> dict[str, str]:
        refresh = RefreshToken.for_user(user)
        return {"access": str(refresh.access_token), "refresh": str(refresh)}

    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict[str, str]:
        """Validate a refresh token and issue a new access token.

        Delegates to SimpleJWT's own ``TokenRefreshSerializer`` so rotation
        and blacklisting (``ROTATE_REFRESH_TOKENS`` / ``BLACKLIST_AFTER_ROTATION``)
        behave exactly as configured in ``settings.SIMPLE_JWT``.
        """
        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except (InvalidToken, TokenError) as exc:
            raise ServiceError("Refresh token is invalid or expired.", "TOKEN_EXPIRED") from exc
        return dict(serializer.validated_data)

    @staticmethod
    def blacklist_token(refresh_token: str) -> None:
        try:
            RefreshToken(refresh_token).blacklist()  # type: ignore[arg-type]
        except TokenError as exc:
            raise ServiceError(
                "Refresh token is invalid or already expired.", "TOKEN_EXPIRED"
            ) from exc


class AuthenticationService(BaseService):
    """Signup (PIN set-up), login (phone + PIN) and PIN changes."""

    @classmethod
    def signup(cls, *, phone_number: str, pin: str, name: str) -> dict[str, Any]:
        user = UserService.get_by_phone_number(phone_number)

        if user is None:
            raise NotInvitedError()
        if user.status != MemberStatus.PENDING:
            raise AlreadyRegisteredError()

        with transaction.atomic():
            user.name = name
            user.set_password(pin)
            user.status = MemberStatus.ACTIVE
            user.is_active = True
            user.save(update_fields=["name", "password", "status", "is_active"])

            Invitation.objects.filter(
                phone_number=phone_number, status=InvitationStatus.PENDING
            ).update(status=InvitationStatus.ACCEPTED, accepted_at=timezone.now())

        tokens = TokenService.issue_tokens_for_user(user)
        return {**tokens, "user": user}

    @classmethod
    def login(cls, *, phone_number: str, pin: str) -> dict[str, Any]:
        user = UserService.get_by_phone_number(phone_number)

        if user is None:
            raise InvalidCredentialsError()
        if user.status == MemberStatus.PENDING:
            raise AccountPendingError()
        if user.status == MemberStatus.SUSPENDED:
            raise AccountSuspendedError(
                f"This account has been suspended: {user.suspension_reason}"
                if user.suspension_reason
                else None
            )
        if user.status == MemberStatus.INACTIVE:
            raise AccountInactiveError()
        if not user.check_password(pin):
            raise InvalidCredentialsError()

        tokens = TokenService.issue_tokens_for_user(user)
        return {**tokens, "user": user}

    @staticmethod
    def change_pin(user: User, old_pin: str, new_pin: str) -> None:
        if not user.check_password(old_pin):
            raise InvalidCredentialsError("Current PIN is incorrect.")
        with transaction.atomic():
            user.set_password(new_pin)
            user.save(update_fields=["password"])
