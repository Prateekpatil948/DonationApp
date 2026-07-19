"""Idempotently provision a superuser from DJANGO_SUPERUSER_* env vars.

Safe to run on every deploy/startup across any environment: if the vars
aren't set, or a user with that email already exists, it's a no-op.
"""

import os

from django.core.management.base import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    help = "Create a superuser from DJANGO_SUPERUSER_* environment variables, if one doesn't already exist."

    def handle(self, *args: object, **options: object) -> None:
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not email or not password:
            self.stdout.write(
                "DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD not set, skipping superuser bootstrap."
            )
            return

        if User.objects.filter(email__iexact=email).exists():
            self.stdout.write(f"Superuser '{email}' already exists, skipping.")
            return

        User.objects.create_superuser(
            email=email,
            password=password,
            phone_number=os.environ.get("DJANGO_SUPERUSER_PHONE_NUMBER", "+10000000000"),
            user_type=os.environ.get("DJANGO_SUPERUSER_USER_TYPE", "ANALYST"),
        )
        self.stdout.write(self.style.SUCCESS(f"Superuser '{email}' created."))
