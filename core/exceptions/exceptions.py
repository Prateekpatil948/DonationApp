"""Custom application-level exceptions raised from the service layer."""

from core.constants.choices import ErrorCode


class ApplicationError(Exception):
    """Base exception for all predictable, service-layer errors.

    Raised from services and translated into a uniform API response by
    ``core.exceptions.handlers.custom_exception_handler``.
    """

    default_message = "An unexpected error occurred."
    error_code: str = ErrorCode.INTERNAL_ERROR
    status_code = 500

    def __init__(self, message: str | None = None, error_code: str | None = None) -> None:
        self.message = message or self.default_message
        self.error_code = error_code or self.error_code
        super().__init__(self.message)


class ServiceError(ApplicationError):
    """Generic error raised by the service layer for business rule violations."""

    default_message = "Unable to complete the requested operation."
    error_code = ErrorCode.VALIDATION_ERROR
    status_code = 400


class InvalidGoogleTokenError(ApplicationError):
    """Raised when a Google ID token fails verification."""

    default_message = "Google token is invalid or expired."
    error_code = ErrorCode.INVALID_TOKEN
    status_code = 401
