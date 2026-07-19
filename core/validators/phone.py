"""Phone number validation shared by serializers."""

import re

from django.core.exceptions import ValidationError

PHONE_REGEX = re.compile(r"^\+?[1-9]\d{7,14}$")


def validate_phone_number(value: str) -> None:
    """Validate E.164-ish phone numbers: optional leading ``+``, 8-15 digits."""
    if not value:
        return
    if not PHONE_REGEX.match(value):
        raise ValidationError(
            "Enter a valid phone number, e.g. +919876543210.",
            code="invalid_phone_number",
        )
