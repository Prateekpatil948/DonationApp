from django.apps import AppConfig


class DonationsConfig(AppConfig):
    """Donation categories, goals and donation entries."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.donations"
    label = "donations"
    verbose_name = "Donations"
