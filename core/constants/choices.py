"""Shared enums / choice constants used across apps."""

from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    MEMBER = "MEMBER", "Member"


class MemberStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACTIVE = "ACTIVE", "Active"
    SUSPENDED = "SUSPENDED", "Suspended"
    INACTIVE = "INACTIVE", "Inactive"


class InvitationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    CANCELLED = "CANCELLED", "Cancelled"


class PaymentMode(models.TextChoices):
    CASH = "CASH", "Cash"
    UPI = "UPI", "UPI"


class ReceiptLanguage(models.TextChoices):
    EN = "EN", "English"
    KN = "KN", "Kannada"
    MR = "MR", "Marathi"


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
    NOT_INVITED = "NOT_INVITED", "Phone Number Not Invited"
    ALREADY_REGISTERED = "ALREADY_REGISTERED", "Phone Number Already Registered"
    DUPLICATE_INVITATION = "DUPLICATE_INVITATION", "Duplicate Invitation"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS", "Invalid Credentials"
    ACCOUNT_PENDING = "ACCOUNT_PENDING", "Account Signup Not Completed"
    ACCOUNT_SUSPENDED = "ACCOUNT_SUSPENDED", "Account Suspended"
    ACCOUNT_INACTIVE = "ACCOUNT_INACTIVE", "Account Inactive"
