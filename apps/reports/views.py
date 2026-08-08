"""Views for the reports app: JSON reports with optional CSV/Excel/PDF export."""

from django.http import HttpResponse

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reports.exports import build_export_response
from apps.reports.serializers import (
    CategoryReportRowSerializer,
    DateReportRowSerializer,
    MemberReportRowSerializer,
    SummaryReportResponseSerializer,
)
from apps.reports.services import ReportService
from core.permissions.roles import IsAdminRole
from utils.response import success_response

REPORT_FILTER_PARAMETERS = [
    OpenApiParameter("date_from", str, required=False),
    OpenApiParameter("date_to", str, required=False),
    OpenApiParameter("category", str, required=False),
    OpenApiParameter("member", str, required=False),
    OpenApiParameter("payment_mode", str, required=False),
    OpenApiParameter("export", str, required=False, description="csv | excel | pdf"),
]


def _filters_from_request(request: Request) -> dict:
    params = request.query_params
    return {
        "date_from": params.get("date_from"),
        "date_to": params.get("date_to"),
        "category": params.get("category"),
        "member": params.get("member"),
        "payment_mode": params.get("payment_mode"),
    }


class SummaryReportView(APIView):
    """``GET /api/v1/reports/summary`` - total collection, cash vs UPI, donation count."""

    permission_classes = [IsAdminRole]

    @extend_schema(
        summary="Collection summary report",
        parameters=REPORT_FILTER_PARAMETERS,
        responses={200: SummaryReportResponseSerializer},
    )
    def get(self, request: Request) -> Response | HttpResponse:
        data = ReportService.summary(_filters_from_request(request))
        export = build_export_response(
            request.query_params.get("export"), "Collection Summary", [data], "summary_report"
        )
        return export or success_response(data)


class CategoryReportView(APIView):
    """``GET /api/v1/reports/category`` - category-wise collection with goal progress."""

    permission_classes = [IsAdminRole]

    @extend_schema(
        summary="Category-wise report",
        parameters=REPORT_FILTER_PARAMETERS,
        responses={200: CategoryReportRowSerializer(many=True)},
    )
    def get(self, request: Request) -> Response | HttpResponse:
        rows = ReportService.by_category(_filters_from_request(request))
        export = build_export_response(
            request.query_params.get("export"), "Category-wise Report", rows, "category_report"
        )
        return export or success_response(rows)


class MemberReportView(APIView):
    """``GET /api/v1/reports/member`` - member-wise collection."""

    permission_classes = [IsAdminRole]

    @extend_schema(
        summary="Member-wise report",
        parameters=REPORT_FILTER_PARAMETERS,
        responses={200: MemberReportRowSerializer(many=True)},
    )
    def get(self, request: Request) -> Response | HttpResponse:
        rows = ReportService.by_member(_filters_from_request(request))
        export = build_export_response(
            request.query_params.get("export"), "Member-wise Report", rows, "member_report"
        )
        return export or success_response(rows)


class DateReportView(APIView):
    """``GET /api/v1/reports/date`` - day-wise collection within a date range."""

    permission_classes = [IsAdminRole]

    @extend_schema(
        summary="Date-wise report",
        parameters=REPORT_FILTER_PARAMETERS,
        responses={200: DateReportRowSerializer(many=True)},
    )
    def get(self, request: Request) -> Response | HttpResponse:
        rows = ReportService.by_date(_filters_from_request(request))
        export = build_export_response(
            request.query_params.get("export"), "Date-wise Report", rows, "date_report"
        )
        return export or success_response(rows)
