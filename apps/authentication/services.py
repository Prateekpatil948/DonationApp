"""Business logic for the authentication app.

``GoogleAuthService`` verifies Google ID tokens, ``TokenService`` issues and
manages JWTs, and the login orchestration itself lives in
``AuthenticationService`` so the view stays a thin authenticate/validate/
invoke/respond layer.
"""

import logging
from typing import Any

from django.conf import settings

from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.services import UserService
from core.exceptions.exceptions import InvalidGoogleTokenError, ServiceError
from services.base import BaseService

logger = logging.getLogger(__name__)


class GoogleAuthService(BaseService):
    """Verifies Google ID tokens issued to the Android client."""

    @staticmethod
    def verify_id_token(id_token_value: str) -> dict[str, Any]:
        try:
            claims = google_id_token.verify_oauth2_token(
                id_token_value,
                google_requests.Request(),
                audience=settings.GOOGLE_CLIENT_ID,
            )
        except (ValueError, GoogleAuthError) as exc:
            logger.warning("google_token_verification_failed", extra={"reason": str(exc)})
            raise InvalidGoogleTokenError() from exc

        if not claims.get("email_verified", True):
            raise InvalidGoogleTokenError("Google email is not verified.")

        return claims


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
    """Orchestrates the full Google login flow: verify -> find-or-create -> issue tokens."""

    @classmethod
    def login_with_google(
        cls, *, id_token_value: str, phone_number: str, user_type: str
    ) -> dict[str, Any]:
        claims = GoogleAuthService.verify_id_token(id_token_value)
        google_id = claims["sub"]
        email = claims["email"]

        user = UserService.get_by_google_id(google_id) or UserService.get_by_email(email)

        if user is None:
            user = UserService.create_from_google_profile(
                email=email,
                google_id=google_id,
                first_name=claims.get("given_name", ""),
                last_name=claims.get("family_name", ""),
                profile_picture=claims.get("picture", ""),
                phone_number=phone_number,
                user_type=user_type,
            )

        tokens = TokenService.issue_tokens_for_user(user)
        return {**tokens, "user": user}
