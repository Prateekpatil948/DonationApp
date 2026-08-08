from django.contrib import admin

from apps.donations.models import Donation, DonationCategory


@admin.register(DonationCategory)
class DonationCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "goal_amount", "sort_order"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    ordering = ["sort_order", "name"]


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = [
        "receipt_number",
        "donor_name",
        "category",
        "amount",
        "payment_mode",
        "donation_date",
        "collected_by",
    ]
    list_filter = ["payment_mode", "category", "donation_date"]
    search_fields = ["receipt_number", "donor_name", "donor_phone", "utr_number"]
    readonly_fields = ["id", "receipt_number", "created_at", "updated_at"]
    date_hierarchy = "donation_date"
