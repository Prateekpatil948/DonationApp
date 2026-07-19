"""Cross-cutting views that don't belong to any single app (e.g. health check)."""

import time

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.utils import OperationalError

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

_START_TIME = time.monotonic()


def _check_database() -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except OperationalError:
        return False


def _check_cache() -> bool:
    try:
        cache.set("health_check", "ok", timeout=5)
        return cache.get("health_check") == "ok"
    except Exception:  # noqa: BLE001 - cache backend errors vary by driver
        return False


class HealthCheckView(APIView):
    """Unauthenticated liveness/readiness probe for load balancers and orchestrators."""

    permission_classes = [AllowAny]
    authentication_classes: list = []

    @extend_schema(
        summary="Health check",
        description="Reports database, cache, application and version status.",
        responses={200: dict, 503: dict},
    )
    def get(self, request: Request) -> Response:
        database_up = _check_database()
        cache_up = _check_cache()
        healthy = database_up and cache_up

        payload = {
            "database": "up" if database_up else "down",
            "cache": "up" if cache_up else "down",
            "application": "up",
            "version": settings.APP_VERSION,
            "uptime_seconds": round(time.monotonic() - _START_TIME, 2),
        }
        return Response(payload, status=200 if healthy else 503)
