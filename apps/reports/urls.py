from django.urls import path

from apps.reports.views import (
    CategoryReportView,
    DateReportView,
    MemberReportView,
    SummaryReportView,
)

app_name = "reports"

urlpatterns = [
    path("summary", SummaryReportView.as_view(), name="summary"),
    path("category", CategoryReportView.as_view(), name="category"),
    path("member", MemberReportView.as_view(), name="member"),
    path("date", DateReportView.as_view(), name="date"),
]
