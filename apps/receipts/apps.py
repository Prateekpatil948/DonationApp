from django.apps import AppConfig


class ReceiptsConfig(AppConfig):
    """Receipt templates and multi-language PDF generation."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.receipts"
    label = "receipts"
    verbose_name = "Receipts"
