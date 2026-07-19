"""Shared enums / choice constants used across apps."""

from django.db import models


class UserType(models.TextChoices):
    ANALYST = "ANALYST", "Analyst"
    SUBSCRIBER = "SUBSCRIBER", "Subscriber"


class ErrorCode(models.TextChoices):
    VALIDATION_ERROR = "VALIDATION_ERROR", "Validation Error"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR", "Authentication Error"
    INVALID_TOKEN = "INVALID_TOKEN", "Invalid Token"
    TOKEN_EXPIRED = "TOKEN_EXPIRED", "Token Expired"
    PERMISSION_DENIED = "PERMISSION_DENIED", "Permission Denied"
    NOT_FOUND = "NOT_FOUND", "Not Found"
    INTEGRITY_ERROR = "INTEGRITY_ERROR", "Integrity Error"
    THROTTLED = "THROTTLED", "Throttled"
    INTERNAL_ERROR = "INTERNAL_ERROR", "Internal Server Error"
