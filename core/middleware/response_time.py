"""Measure and expose request handling duration."""

import time
from typing import Callable

from django.http import HttpRequest, HttpResponse

RESPONSE_TIME_HEADER = "X-Response-Time-Ms"


class ResponseTimeMiddleware:
    """Attach the request handling duration (ms) to every response."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = (time.monotonic() - start) * 1000
        request.response_time_ms = duration_ms  # type: ignore[attr-defined]
        response[RESPONSE_TIME_HEADER] = f"{duration_ms:.2f}"
        return response
