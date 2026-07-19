"""Helpers that build the project's uniform API response envelope."""

from typing import Any

from rest_framework.response import Response


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
) -> Response:
    """Build a standard success envelope: ``{"success": true, "message", "data"}``."""
    return Response(
        {"success": True, "message": message, "data": data},
        status=status_code,
    )


def error_response(
    code: str,
    message: str,
    status_code: int = 400,
    details: Any = None,
) -> Response:
    """Build a standard error envelope: ``{"success": false, "error": {"code", "message"}}``."""
    error: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return Response({"success": False, "error": error}, status=status_code)
