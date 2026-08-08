"""Views for the donations app: categories and donation entries."""

from typing import cast

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.donations.models import Donation
from apps.donations.serializers import (
    CategoryResponseSerializer,
    CategoryWriteRequestSerializer,
    DonationCreateRequestSerializer,
    DonationResponseSerializer,
    DonationUpdateRequestSerializer,
)
from apps.donations.services import CategoryService, DonationService
from apps.users.models import User
from core.constants.choices import UserRole
from core.pagination.pagination import StandardResultsSetPagination
from core.permissions.roles import IsActiveMember, IsAdminRole
from utils.response import success_response


class CategoryListCreateView(APIView):
    """``GET/POST /api/v1/categories/`` - list (any active member) / create (admin only)."""

    def get_permissions(self) -> list:
        if self.request.method == "POST":
            return [IsAdminRole()]
        return [IsActiveMember()]

    @extend_schema(
        summary="List donation categories",
        operation_id="categories_list",
        parameters=[OpenApiParameter("is_active", bool, required=False)],
        responses={200: CategoryResponseSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        is_active_param = request.query_params.get("is_active")
        is_active = None
        if is_active_param is not None:
            is_active = is_active_param.lower() in ("true", "1")

        categories = CategoryService.list({"is_active": is_active})
        serializer = CategoryResponseSerializer(categories, many=True)
        return success_response(serializer.data)

    @extend_schema(
        summary="Create a donation category",
        request=CategoryWriteRequestSerializer,
        responses={201: CategoryResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = CategoryWriteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category = CategoryService.create(cast(User, request.user), serializer.validated_data)
        return success_response(
            CategoryResponseSerializer(category).data,
            message="Category created",
            status_code=201,
        )


class CategoryDetailView(APIView):
    """``GET/PUT/PATCH /api/v1/categories/{id}/`` - view (any member) / edit (admin only)."""

    def get_permissions(self) -> list:
        if self.request.method in ("PUT", "PATCH"):
            return [IsAdminRole()]
        return [IsActiveMember()]

    @extend_schema(
        summary="Get a donation category",
        operation_id="categories_retrieve",
        responses={200: CategoryResponseSerializer},
    )
    def get(self, request: Request, pk: str) -> Response:
        category = CategoryService.get_by_id(pk)
        return success_response(CategoryResponseSerializer(category).data)

    @extend_schema(
        summary="Update a donation category",
        request=CategoryWriteRequestSerializer,
        responses={200: CategoryResponseSerializer},
    )
    def put(self, request: Request, pk: str) -> Response:
        return self._update(request, pk)

    @extend_schema(
        summary="Partially update a donation category",
        request=CategoryWriteRequestSerializer,
        responses={200: CategoryResponseSerializer},
    )
    def patch(self, request: Request, pk: str) -> Response:
        return self._update(request, pk)

    def _update(self, request: Request, pk: str) -> Response:
        category = CategoryService.get_by_id(pk)
        serializer = CategoryWriteRequestSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        category = CategoryService.update(
            cast(User, request.user), category, serializer.validated_data
        )
        return success_response(
            CategoryResponseSerializer(category).data, message="Category updated"
        )


class DonationListCreateView(ListAPIView):
    """``GET/POST /api/v1/donations/`` - list own/all donations, record a new one."""

    permission_classes = [IsActiveMember]
    serializer_class = DonationResponseSerializer
    pagination_class = StandardResultsSetPagination

    @extend_schema(
        summary="List donations",
        parameters=[
            OpenApiParameter("category", str, required=False),
            OpenApiParameter("payment_mode", str, required=False),
            OpenApiParameter("collected_by", str, required=False, description="Admin only"),
            OpenApiParameter("date_from", str, required=False),
            OpenApiParameter("date_to", str, required=False),
            OpenApiParameter(
                "search", str, required=False, description="donor name/phone/receipt no."
            ),
        ],
    )
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Donation.objects.none()

        params = self.request.query_params
        return DonationService.list(
            self.request.user,
            {
                "category": params.get("category"),
                "payment_mode": params.get("payment_mode"),
                "collected_by": params.get("collected_by"),
                "date_from": params.get("date_from"),
                "date_to": params.get("date_to"),
                "search": params.get("search"),
            },
        )

    @extend_schema(
        summary="Record a donation",
        request=DonationCreateRequestSerializer,
        responses={201: DonationResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = DonationCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        donation = DonationService.create(cast(User, request.user), dict(serializer.validated_data))
        return success_response(
            DonationResponseSerializer(donation).data, message="Donation recorded", status_code=201
        )


class DonationDetailView(APIView):
    """``GET/PUT/PATCH /api/v1/donations/{id}/`` - the owning member or an admin only."""

    permission_classes = [IsActiveMember]

    def _get_donation_or_403(self, request: Request, pk: str) -> Donation:
        user = cast(User, request.user)
        donation = DonationService.get_by_id(pk)
        if user.role != UserRole.ADMIN and donation.collected_by_id != user.id:
            raise PermissionDenied("You may only access your own donation entries.")
        return donation

    @extend_schema(summary="Get a donation", responses={200: DonationResponseSerializer})
    def get(self, request: Request, pk: str) -> Response:
        donation = self._get_donation_or_403(request, pk)
        return success_response(DonationResponseSerializer(donation).data)

    @extend_schema(
        summary="Update a donation",
        request=DonationUpdateRequestSerializer,
        responses={200: DonationResponseSerializer},
    )
    def put(self, request: Request, pk: str) -> Response:
        return self._update(request, pk)

    @extend_schema(
        summary="Partially update a donation",
        request=DonationUpdateRequestSerializer,
        responses={200: DonationResponseSerializer},
    )
    def patch(self, request: Request, pk: str) -> Response:
        return self._update(request, pk)

    def _update(self, request: Request, pk: str) -> Response:
        donation = self._get_donation_or_403(request, pk)
        serializer = DonationUpdateRequestSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        donation = DonationService.update(
            cast(User, request.user), donation, dict(serializer.validated_data)
        )
        return success_response(
            DonationResponseSerializer(donation).data, message="Donation updated"
        )
