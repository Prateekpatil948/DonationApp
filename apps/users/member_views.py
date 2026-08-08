"""Views for admin-only member management: invite, list, suspend, reactivate, deactivate."""

from typing import cast

from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers import (
    InvitationResponseSerializer,
    InviteMemberRequestSerializer,
    MemberReasonRequestSerializer,
    UserResponseSerializer,
)
from apps.users.services import InvitationService, UserService
from core.pagination.pagination import StandardResultsSetPagination
from core.permissions.roles import IsAdminRole
from utils.response import success_response


class InviteMemberView(APIView):
    """``POST /api/v1/members/invite`` - invite a phone number to join as admin/member."""

    permission_classes = [IsAdminRole]

    @extend_schema(
        summary="Invite a member",
        request=InviteMemberRequestSerializer,
        responses={200: InvitationResponseSerializer},
        examples=[
            OpenApiExample(
                "Request",
                value={"phone_number": "+919876543210", "role": "MEMBER"},
                request_only=True,
            ),
        ],
    )
    def post(self, request: Request) -> Response:
        serializer = InviteMemberRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invitation = InvitationService.invite(
            actor=cast(User, request.user),
            phone_number=serializer.validated_data["phone_number"],
            role=serializer.validated_data["role"],
        )
        return success_response(
            InvitationResponseSerializer(invitation).data, message="Invitation sent"
        )


class MemberListView(ListAPIView):
    """``GET /api/v1/members/`` - paginated, filterable list of members (admin only)."""

    permission_classes = [IsAdminRole]
    serializer_class = UserResponseSerializer
    pagination_class = StandardResultsSetPagination

    @extend_schema(
        summary="List members",
        parameters=[
            OpenApiParameter(
                "status", str, description="Filter by PENDING/ACTIVE/SUSPENDED/INACTIVE"
            ),
            OpenApiParameter("role", str, description="Filter by ADMIN/MEMBER"),
            OpenApiParameter("search", str, description="Search by name or phone number"),
        ],
    )
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return UserService.list_members(
            {
                "status": self.request.query_params.get("status"),
                "role": self.request.query_params.get("role"),
                "search": self.request.query_params.get("search"),
            }
        )


class MemberDetailView(RetrieveAPIView):
    """``GET /api/v1/members/{id}/`` - fetch a single member (admin only)."""

    permission_classes = [IsAdminRole]
    serializer_class = UserResponseSerializer
    queryset = User.objects.all()

    @extend_schema(summary="Get member detail")
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().get(request, *args, **kwargs)


class _MemberActionView(APIView):
    """Shared base for the suspend/reactivate/deactivate reason-gated actions."""

    permission_classes = [IsAdminRole]
    action_method_name = ""
    success_message = ""

    def post(self, request: Request, pk: str) -> Response:
        serializer = MemberReasonRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        member = UserService.get_by_id(pk)
        action = getattr(UserService, self.action_method_name)
        member = action(request.user, member, serializer.validated_data["reason"])

        return success_response(UserResponseSerializer(member).data, message=self.success_message)


class SuspendMemberView(_MemberActionView):
    """``POST /api/v1/members/{id}/suspend`` - suspend a member with a mandatory reason."""

    action_method_name = "suspend"
    success_message = "Member suspended"

    @extend_schema(
        summary="Suspend a member",
        request=MemberReasonRequestSerializer,
        responses={200: UserResponseSerializer},
    )
    def post(self, request: Request, pk: str) -> Response:
        return super().post(request, pk)


class ReactivateMemberView(_MemberActionView):
    """``POST /api/v1/members/{id}/reactivate`` - reactivate a suspended/inactive member."""

    action_method_name = "reactivate"
    success_message = "Member reactivated"

    @extend_schema(
        summary="Reactivate a member",
        request=MemberReasonRequestSerializer,
        responses={200: UserResponseSerializer},
    )
    def post(self, request: Request, pk: str) -> Response:
        return super().post(request, pk)


class DeactivateMemberView(_MemberActionView):
    """``POST /api/v1/members/{id}/deactivate`` - mark a member inactive."""

    action_method_name = "deactivate"
    success_message = "Member deactivated"

    @extend_schema(
        summary="Deactivate a member",
        request=MemberReasonRequestSerializer,
        responses={200: UserResponseSerializer},
    )
    def post(self, request: Request, pk: str) -> Response:
        return super().post(request, pk)
