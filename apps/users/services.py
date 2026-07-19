"""Business logic for the users app. Views must never touch the ORM directly."""

from typing import Any

from django.db import transaction

from apps.users.models import User
from services.base import BaseService

EDITABLE_PROFILE_FIELDS = ("first_name", "last_name", "phone_number", "profile_picture")


class UserService(BaseService):
    """Encapsulates all read/write operations on ``User``."""

    @staticmethod
    def get_by_id(user_id: str) -> User:
        return User.objects.get(id=user_id)

    @staticmethod
    def get_by_google_id(google_id: str) -> User | None:
        return User.objects.filter(google_id=google_id).first()

    @staticmethod
    def get_by_email(email: str) -> User | None:
        return User.objects.filter(email=email).first()

    @classmethod
    def create_from_google_profile(
        cls,
        *,
        email: str,
        google_id: str,
        first_name: str,
        last_name: str,
        profile_picture: str,
        phone_number: str,
        user_type: str,
    ) -> User:
        with transaction.atomic():
            return User.objects.create(
                email=email,
                google_id=google_id,
                first_name=first_name,
                last_name=last_name,
                profile_picture=profile_picture,
                phone_number=phone_number,
                user_type=user_type,
                is_verified=True,
            )

    @classmethod
    def update_profile(cls, user: User, validated_data: dict[str, Any]) -> User:
        fields_to_update = []
        for field in EDITABLE_PROFILE_FIELDS:
            if field in validated_data:
                setattr(user, field, validated_data[field])
                fields_to_update.append(field)

        if fields_to_update:
            with transaction.atomic():
                user.save(update_fields=fields_to_update)
        return user
