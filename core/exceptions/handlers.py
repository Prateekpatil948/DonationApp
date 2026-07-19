"""Global DRF exception handler mapping every error to a uniform response."""

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.db import IntegrityError
from django.http import Http404

from rest_framework import exceptions as drf_exceptions
from rest_framework.views import exception_handler as drf_exception_handler

from core.constants.choices import ErrorCode
from core.exceptions.exceptions import ApplicationError
from utils.response import error_response

logger = logging.getLogger(__name__)


def _flatten_validation_errors(detail: object) -> str:
    """Collapse a DRF validation error detail tree into one readable message."""
    if isinstance(detail, list):
        return "; ".join(_flatten_validation_errors(item) for item in detail)
    if isinstance(detail, dict):
        parts = []
        for field, errors in detail.items():
            parts.append(f"{field}: {_flatten_validation_errors(errors)}")
        return "; ".join(parts)
    return str(detail)


def custom_exception_handler(exc: Exception, context: dict) -> object:
    """Translate any exception raised in a view into the standard error envelope.

    Order matters: application-level errors are checked first since they carry
    their own status code and error code; everything else falls back to DRF's
    default handler (which normalizes Django's ``Http404``/``PermissionDenied``
    into DRF exceptions) before being re-shaped into the uniform response.
    """
    request = context.get("request")

    if isinstance(exc, ApplicationError):
        logger.warning(
            "application_error",
            extra={"error_code": exc.error_code, "path": getattr(request, "path", None)},
        )
        return error_response(exc.error_code, exc.message, exc.status_code)

    if isinstance(exc, (Http404, ObjectDoesNotExist)):
        exc = drf_exceptions.NotFound()

    if isinstance(exc, DjangoPermissionDenied):
        exc = drf_exceptions.PermissionDenied()

    if isinstance(exc, IntegrityError):
        logger.error("integrity_error", exc_info=True)
        return error_response(
            ErrorCode.INTEGRITY_ERROR,
            "A database integrity error occurred.",
            409,
        )

    response = drf_exception_handler(exc, context)

    if response is None:
        logger.error("unhandled_exception", exc_info=True)
        return error_response(
            ErrorCode.INTERNAL_ERROR,
            "An unexpected error occurred. Please try again later.",
            500,
        )

    code = ErrorCode.VALIDATION_ERROR
    message = _flatten_validation_errors(response.data.get("detail", response.data))

    if isinstance(exc, drf_exceptions.AuthenticationFailed):
        code = ErrorCode.AUTHENTICATION_ERROR
    elif isinstance(exc, drf_exceptions.NotAuthenticated):
        code = ErrorCode.AUTHENTICATION_ERROR
    elif isinstance(exc, drf_exceptions.PermissionDenied):
        code = ErrorCode.PERMISSION_DENIED
    elif isinstance(exc, drf_exceptions.NotFound):
        code = ErrorCode.NOT_FOUND
    elif isinstance(exc, drf_exceptions.Throttled):
        code = ErrorCode.THROTTLED
        wait = exc.wait  # type: ignore[attr-defined]
        message = f"Request was throttled. Try again in {wait} seconds."
    elif isinstance(exc, drf_exceptions.ValidationError):
        code = ErrorCode.VALIDATION_ERROR

    logger.warning(
        "api_error",
        extra={"error_code": code, "status_code": response.status_code},
    )
    return error_response(code, message, response.status_code, details=response.data)
