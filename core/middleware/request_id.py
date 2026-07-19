"""Attach a unique request ID to every incoming request/outgoing response."""

import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware:
    """Ensure every request carries a request ID, generating one if absent."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.request_id = request.headers.get(  # type: ignore[attr-defined]
            REQUEST_ID_HEADER, str(uuid.uuid4())
        )
        response = self.get_response(request)
        response[REQUEST_ID_HEADER] = request.request_id  # type: ignore[attr-defined]
        return response
