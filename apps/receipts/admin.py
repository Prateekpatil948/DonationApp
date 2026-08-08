from django.contrib import admin

from apps.receipts.models import ReceiptTemplate


@admin.register(ReceiptTemplate)
class ReceiptTemplateAdmin(admin.ModelAdmin):
    list_display = ["language", "is_active", "show_signature_line"]
    list_filter = ["is_active"]
