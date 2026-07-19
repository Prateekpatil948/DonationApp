"""Views for the authentication app: authenticate, validate, invoke service, respond."""

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.authentication.serializers import (
    GoogleLoginRequestSerializer,
    LogoutRequestSerializer,
    TokenPairResponseSerializer,
    TokenRefreshRequestSerializer,
    TokenRefreshResponseSerializer,
)
from apps.authentication.services import AuthenticationService, TokenService
from apps.users.serializers import UserResponseSerializer
from utils.response import success_response


class GoogleLoginView(APIView):
    """``POST /api/v1/auth/google/login`` - verify Google token, login or sign up."""

    permission_classes = [AllowAny]
    authentication_classes: list = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "google_login"

    @extend_schema(
        summary="Login or sign up with Google",
        request=GoogleLoginRequestSerializer,
        responses={200: TokenPairResponseSerializer, 401: dict},
        examples=[
            OpenApiExample(
                "Request",
                value={
                    "id_token": "eyJhbGciOi...",
                    "phone_number": "+919876543210",
                    "user_type": "ANALYST",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Response",
                value={
                    "success": True,
                    "message": "Login successful",
                    "data": {
                        "access": "eyJhbGciOi...",
                        "refresh": "eyJhbGciOi...",
                        "user": {"id": "...", "email": "analyst@example.com"},
                    },
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request: Request) -> Response:
        request_serializer = GoogleLoginRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        result = AuthenticationService.login_with_google(
            id_token_value=request_serializer.validated_data["id_token"],
            phone_number=request_serializer.validated_data["phone_number"],
            user_type=request_serializer.validated_data["user_type"],
        )

        payload = {
            "access": result["access"],
            "refresh": result["refresh"],
            "user": UserResponseSerializer(result["user"]).data,
        }
        return success_response(payload, message="Login successful")


class LogoutView(APIView):
    """``POST /api/v1/auth/logout`` - blacklist the supplied refresh token."""

    permission_classes = [AllowAny]
    authentication_classes: list = []

    @extend_schema(
        summary="Logout",
        request=LogoutRequestSerializer,
        responses={200: dict},
    )
    def post(self, request: Request) -> Response:
        serializer = LogoutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        TokenService.blacklist_token(serializer.validated_data["refresh"])
        return success_response(message="Logout successful")


class TokenRefreshView(APIView):
    """``POST /api/v1/auth/refresh`` - exchange a refresh token for a new access token."""

    permission_classes = [AllowAny]
    authentication_classes: list = []

    @extend_schema(
        summary="Refresh access token",
        request=TokenRefreshRequestSerializer,
        responses={200: TokenRefreshResponseSerializer, 401: dict},
    )
    def post(self, request: Request) -> Response:
        serializer = TokenRefreshRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = TokenService.refresh_access_token(serializer.validated_data["refresh"])
        return success_response(tokens, message="Token refreshed successfully")
