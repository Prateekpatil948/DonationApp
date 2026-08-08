"""Root URL configuration."""

from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from core.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", HealthCheckView.as_view(), name="health-check"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/members/", include("apps.users.member_urls")),
    path("api/v1/categories/", include("apps.donations.urls")),
    path("api/v1/donations/", include("apps.donations.donation_urls")),
    path("api/v1/receipts/", include("apps.receipts.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
    path("api/v1/temple-settings/", include("apps.common.urls")),
]
