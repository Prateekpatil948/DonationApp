"""Per-language receipt header/footer configuration."""

from django.db import models

from apps.common.models import BaseModel
from core.constants.choices import ReceiptLanguage


class ReceiptTemplate(BaseModel):
    """Header/footer text for one receipt language, configurable by the admin."""

    language = models.CharField(max_length=5, choices=ReceiptLanguage.choices, unique=True)
    header_text = models.TextField(blank=True, default="")
    footer_text = models.TextField(blank=True, default="")
    show_signature_line = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        db_table = "receipt_templates"
        ordering = ["language"]

    def __str__(self) -> str:
        return f"ReceiptTemplate({self.language})"
