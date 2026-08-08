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


class NotInvitedError(ApplicationError):
    """Raised on signup when the phone number has no pending invitation."""

    default_message = "This phone number has not been invited to join."
    error_code = ErrorCode.NOT_INVITED
    status_code = 403


class AlreadyRegisteredError(ApplicationError):
    """Raised on signup when the phone number has already completed signup."""

    default_message = "This phone number is already registered. Please log in instead."
    error_code = ErrorCode.ALREADY_REGISTERED
    status_code = 409


class DuplicateInvitationError(ApplicationError):
    """Raised when inviting a phone number that already has an active user or invite."""

    default_message = "This phone number has already been invited or registered."
    error_code = ErrorCode.DUPLICATE_INVITATION
    status_code = 409


class InvalidCredentialsError(ApplicationError):
    """Raised on login when the phone number or PIN is incorrect."""

    default_message = "Phone number or PIN is incorrect."
    error_code = ErrorCode.INVALID_CREDENTIALS
    status_code = 401


class AccountPendingError(ApplicationError):
    """Raised on login when the invited user hasn't completed signup yet."""

    default_message = "Please complete signup with your PIN before logging in."
    error_code = ErrorCode.ACCOUNT_PENDING
    status_code = 403


class AccountSuspendedError(ApplicationError):
    """Raised on login when the member account is suspended."""

    default_message = "This account has been suspended."
    error_code = ErrorCode.ACCOUNT_SUSPENDED
    status_code = 403


class AccountInactiveError(ApplicationError):
    """Raised on login when the member account is inactive."""

    default_message = "This account is inactive. Contact your admin."
    error_code = ErrorCode.ACCOUNT_INACTIVE
    status_code = 403
