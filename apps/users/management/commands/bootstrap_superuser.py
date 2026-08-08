"""Idempotently provision the first admin from DJANGO_SUPERUSER_* env vars.

Safe to run on every deploy/startup across any environment: if the vars
aren't set, or a user with that phone number already exists, it's a no-op.
"""

import os

from django.core.management.base import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    help = (
        "Create the first admin from DJANGO_SUPERUSER_* environment variables, "
        "if one doesn't already exist."
    )

    def handle(self, *args: object, **options: object) -> None:
        phone_number = os.environ.get("DJANGO_SUPERUSER_PHONE_NUMBER")
        pin = os.environ.get("DJANGO_SUPERUSER_PIN")

        if not phone_number or not pin:
            self.stdout.write(
                "DJANGO_SUPERUSER_PHONE_NUMBER / DJANGO_SUPERUSER_PIN not set, "
                "skipping superuser bootstrap."
            )
            return

        if User.objects.filter(phone_number=phone_number).exists():
            self.stdout.write(f"Superuser '{phone_number}' already exists, skipping.")
            return

        User.objects.create_superuser(
            phone_number=phone_number,
            pin=pin,
            name=os.environ.get("DJANGO_SUPERUSER_NAME", "Temple Admin"),
        )
        self.stdout.write(self.style.SUCCESS(f"Superuser '{phone_number}' created."))
