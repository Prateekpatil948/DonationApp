"""Views for the receipts app: JSON receipt detail and PDF download."""

from typing import cast

from django.http import HttpResponse

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.donations.models import Donation
from apps.donations.serializers import DonationResponseSerializer
from apps.donations.services import DonationService
from apps.receipts.services import ReceiptPDFService
from apps.users.models import User
from core.constants.choices import UserRole
from core.permissions.roles import IsActiveMember
from utils.response import success_response


def _get_donation_or_403(request: Request, pk: str) -> Donation:
    user = cast(User, request.user)
    donation = DonationService.get_by_id(pk)
    if user.role != UserRole.ADMIN and donation.collected_by_id != user.id:
        raise PermissionDenied("You may only access receipts for your own donation entries.")
    return donation


class ReceiptDetailView(APIView):
    """``GET /api/v1/receipts/{donation_id}/`` - JSON receipt data."""

    permission_classes = [IsActiveMember]

    @extend_schema(summary="Get receipt data", responses={200: DonationResponseSerializer})
    def get(self, request: Request, pk: str) -> Response:
        donation = _get_donation_or_403(request, pk)
        return success_response(DonationResponseSerializer(donation).data)


class ReceiptPDFView(APIView):
    """``GET /api/v1/receipts/{donation_id}/pdf`` - download/print/reprint the PDF."""

    permission_classes = [IsActiveMember]

    @extend_schema(
        summary="Download receipt PDF",
        parameters=[
            OpenApiParameter(
                "language",
                str,
                required=False,
                description="Override language for reprint: EN/KN/MR",
            )
        ],
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request: Request, pk: str) -> HttpResponse:
        donation = _get_donation_or_403(request, pk)
        language = request.query_params.get("language")
        pdf_bytes = ReceiptPDFService.generate(donation, language=language)

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{donation.receipt_number}.pdf"'
        return response
