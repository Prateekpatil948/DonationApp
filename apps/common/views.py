"""Views for the common app: temple settings."""

from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.serializers import (
    TempleSettingsResponseSerializer,
    TempleSettingsUpdateRequestSerializer,
)
from apps.common.services import AuditService, TempleSettingsService
from apps.users.models import User
from core.permissions.roles import IsActiveMember, IsAdminRole
from utils.response import success_response


class TempleSettingsView(APIView):
    """``GET/PUT /api/v1/temple-settings/`` - temple identity/receipt config."""

    def get_permissions(self) -> list:
        if self.request.method == "PUT":
            return [IsAdminRole()]
        return [IsActiveMember()]

    @extend_schema(summary="Get temple settings", responses={200: TempleSettingsResponseSerializer})
    def get(self, request: Request) -> Response:
        settings_row = TempleSettingsService.get_settings()
        return success_response(TempleSettingsResponseSerializer(settings_row).data)

    @extend_schema(
        summary="Update temple settings",
        request=TempleSettingsUpdateRequestSerializer,
        responses={200: TempleSettingsResponseSerializer},
    )
    def put(self, request: Request) -> Response:
        serializer = TempleSettingsUpdateRequestSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        settings_row = TempleSettingsService.update_settings(serializer.validated_data)

        AuditService.log(
            cast(User, request.user),
            "TEMPLE_SETTINGS_UPDATED",
            target=settings_row,
            details=serializer.validated_data,
        )
        return success_response(
            TempleSettingsResponseSerializer(settings_row).data, message="Temple settings updated"
        )
