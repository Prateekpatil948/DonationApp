"""Donation categories (with optional goals) and donation entries."""

from django.conf import settings
from django.db import models

from apps.common.models import BaseModel
from core.constants.choices import PaymentMode, ReceiptLanguage
from core.validators.phone import validate_phone_number


class DonationCategory(BaseModel):
    """Configurable donation category, e.g. Annadanam, Renovation, Hundi."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    color = models.CharField(max_length=7, blank=True, default="#6750A4")
    sort_order = models.IntegerField(default=0)

    class Meta(BaseModel.Meta):
        db_table = "donation_categories"
        ordering = ["sort_order", "name"]
        verbose_name_plural = "Donation categories"

    def __str__(self) -> str:
        return self.name


class Donation(BaseModel):
    """A single donation entry recorded by a member."""

    donation_date = models.DateField()
    donor_name = models.CharField(max_length=150)
    donor_phone = models.CharField(
        max_length=20, blank=True, default="", validators=[validate_phone_number]
    )
    donor_address = models.TextField(blank=True, default="")
    category = models.ForeignKey(
        DonationCategory, on_delete=models.PROTECT, related_name="donations"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(max_length=10, choices=PaymentMode.choices)
    utr_number = models.CharField(max_length=64, blank=True, default="")
    remarks = models.TextField(blank=True, default="")
    receipt_language = models.CharField(
        max_length=5, choices=ReceiptLanguage.choices, default=ReceiptLanguage.EN
    )
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="donations_collected"
    )
    receipt_number = models.CharField(max_length=32, unique=True, editable=False)

    class Meta(BaseModel.Meta):
        db_table = "donations"
        ordering = ["-donation_date", "-created_at"]
        indexes = [
            models.Index(fields=["donation_date"]),
            models.Index(fields=["receipt_number"]),
            models.Index(fields=["payment_mode"]),
        ]

    def __str__(self) -> str:
        return f"{self.receipt_number} - {self.donor_name} ({self.amount})"
