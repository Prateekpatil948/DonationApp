"""Views for the authentication app: authenticate, validate, invoke service, respond."""

from typing import cast

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.authentication.serializers import (
    ChangePinRequestSerializer,
    LoginRequestSerializer,
    LogoutRequestSerializer,
    SignupRequestSerializer,
    TokenPairResponseSerializer,
    TokenRefreshRequestSerializer,
    TokenRefreshResponseSerializer,
)
from apps.authentication.services import AuthenticationService, TokenService
from apps.users.models import User
from apps.users.serializers import UserResponseSerializer
from utils.response import success_response


class SignupView(APIView):
    """``POST /api/v1/auth/signup`` - set a PIN for an invited phone number."""

    permission_classes = [AllowAny]
    authentication_classes: list = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "signup"

    @extend_schema(
        summary="Complete signup with a PIN",
        request=SignupRequestSerializer,
        responses={200: TokenPairResponseSerializer, 403: dict},
        examples=[
            OpenApiExample(
                "Request",
                value={
                    "phone_number": "+919876543210",
                    "pin": "123456",
                    "confirm_pin": "123456",
                    "name": "Ravi Kumar",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request: Request) -> Response:
        serializer = SignupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = AuthenticationService.signup(
            phone_number=serializer.validated_data["phone_number"],
            pin=serializer.validated_data["pin"],
            name=serializer.validated_data["name"],
        )

        payload = {
            "access": result["access"],
            "refresh": result["refresh"],
            "user": UserResponseSerializer(result["user"]).data,
        }
        return success_response(payload, message="Signup successful")


class LoginView(APIView):
    """``POST /api/v1/auth/login`` - phone number + PIN login."""

    permission_classes = [AllowAny]
    authentication_classes: list = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    @extend_schema(
        summary="Login with phone number and PIN",
        request=LoginRequestSerializer,
        responses={200: TokenPairResponseSerializer, 401: dict},
        examples=[
            OpenApiExample(
                "Request",
                value={"phone_number": "+919876543210", "pin": "123456"},
                request_only=True,
            ),
        ],
    )
    def post(self, request: Request) -> Response:
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = AuthenticationService.login(
            phone_number=serializer.validated_data["phone_number"],
            pin=serializer.validated_data["pin"],
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

    @extend_schema(summary="Logout", request=LogoutRequestSerializer, responses={200: dict})
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


class ChangePinView(APIView):
    """``POST /api/v1/auth/change-pin`` - change the caller's own PIN."""

    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Change PIN", request=ChangePinRequestSerializer, responses={200: dict})
    def post(self, request: Request) -> Response:
        serializer = ChangePinRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AuthenticationService.change_pin(
            cast(User, request.user),
            serializer.validated_data["old_pin"],
            serializer.validated_data["new_pin"],
        )
        return success_response(message="PIN changed successfully")
