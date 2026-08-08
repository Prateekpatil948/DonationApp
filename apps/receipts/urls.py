from django.urls import path

from apps.receipts.views import ReceiptDetailView, ReceiptPDFView

app_name = "receipts"

urlpatterns = [
    path("<uuid:pk>/", ReceiptDetailView.as_view(), name="detail"),
    path("<uuid:pk>/pdf", ReceiptPDFView.as_view(), name="pdf"),
]
