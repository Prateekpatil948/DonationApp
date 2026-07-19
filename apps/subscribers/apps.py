from django.apps import AppConfig


class SubscribersConfig(AppConfig):
    """Reserved for subscriber-specific domain models/endpoints (future scope)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.subscribers"
    label = "subscribers"
    verbose_name = "Subscribers"
