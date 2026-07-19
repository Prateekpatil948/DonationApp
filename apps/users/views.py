"""Views for the users app: authenticate, validate, invoke service, respond.

No business logic lives here - see ``apps.users.services.UserService``.
"""

from typing import cast

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers import UserProfileUpdateRequestSerializer, UserResponseSerializer
from apps.users.services import UserService
from utils.response import success_response


class MeView(APIView):
    """``GET/PUT /api/v1/users/me`` - fetch or update the caller's own profile."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get current user profile",
        responses={200: UserResponseSerializer},
        examples=[
            OpenApiExample(
                "Profile",
                value={
                    "success": True,
                    "message": "Profile fetched successfully",
                    "data": {
                        "id": "b3b3b3b3-b3b3-b3b3-b3b3-b3b3b3b3b3b3",
                        "email": "analyst@example.com",
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "profile_picture": "https://example.com/photo.jpg",
                        "phone_number": "+919876543210",
                        "user_type": "ANALYST",
                        "is_active": True,
                        "is_verified": True,
                        "created_at": "2026-01-01T00:00:00.000000Z",
                        "updated_at": "2026-01-01T00:00:00.000000Z",
                    },
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request: Request) -> Response:
        serializer = UserResponseSerializer(request.user)
        return success_response(serializer.data, message="Profile fetched successfully")

    @extend_schema(
        summary="Update current user profile",
        request=UserProfileUpdateRequestSerializer,
        responses={200: UserResponseSerializer},
        examples=[
            OpenApiExample(
                "Update request",
                value={
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "phone_number": "+919876543210",
                    "profile_picture": "https://example.com/photo.jpg",
                },
                request_only=True,
            ),
        ],
    )
    def put(self, request: Request) -> Response:
        request_serializer = UserProfileUpdateRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        user = UserService.update_profile(
            cast(User, request.user), request_serializer.validated_data
        )

        response_serializer = UserResponseSerializer(user)
        return success_response(response_serializer.data, message="Profile updated successfully")
