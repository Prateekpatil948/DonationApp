from django.apps import AppConfig


class ReportsConfig(AppConfig):
    """Admin-facing donation reports: JSON + CSV/Excel/PDF export."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reports"
    label = "reports"
    verbose_name = "Reports"
