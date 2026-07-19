from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """Reserved for analyst-facing reporting/dashboard endpoints (future scope)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analytics"
    label = "analytics"
    verbose_name = "Analytics"
