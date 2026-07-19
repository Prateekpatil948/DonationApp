"""Structured access logging for every request/response cycle."""

import logging
from typing import Callable

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("apps.access")


def _client_ip(request: HttpRequest) -> str:
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


class RequestLoggingMiddleware:
    """Log method, path, status, duration, user and request ID for each request.

    Must sit inside ``RequestIDMiddleware`` and outside ``ResponseTimeMiddleware``
    in ``MIDDLEWARE`` so both ``request.request_id`` and ``request.response_time_ms``
    are populated by the time this logs the response.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        user = getattr(request, "user", None)
        user_id = (
            str(user.id) if user is not None and getattr(user, "is_authenticated", False) else None
        )

        logger.info(
            "request_handled",
            extra={
                "request_id": getattr(request, "request_id", None),
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "response_time_ms": getattr(request, "response_time_ms", None),
                "user_id": user_id,
                "ip": _client_ip(request),
            },
        )
        return response
