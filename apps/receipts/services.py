"""Multi-language PDF receipt generation via WeasyPrint."""

from typing import Any

from django.template.loader import render_to_string

from weasyprint import HTML

from apps.common.services import TempleSettingsService
from apps.donations.models import Donation
from core.constants.choices import ReceiptLanguage
from services.base import BaseService

# Best-effort translations for standard receipt fields. Have a native speaker
# review the Kannada/Marathi strings before relying on them in production.
RECEIPT_LABELS: dict[str, dict[str, str]] = {
    ReceiptLanguage.EN: {
        "title": "Donation Receipt",
        "receipt_no": "Receipt No.",
        "date": "Date",
        "donor_name": "Donor Name",
        "phone": "Phone Number",
        "address": "Address",
        "category": "Category",
        "amount": "Amount",
        "payment_mode": "Payment Mode",
        "cash": "Cash",
        "upi": "UPI",
        "utr": "UTR Number",
        "remarks": "Remarks",
        "collected_by": "Collected By",
        "thank_you": "Thank you for your generous donation.",
        "signature": "Authorized Signatory",
    },
    ReceiptLanguage.KN: {
        "title": "ದೇಣಿಗೆ ರಶೀದಿ",
        "receipt_no": "ರಶೀದಿ ಸಂಖ್ಯೆ",
        "date": "ದಿನಾಂಕ",
        "donor_name": "ದಾನಿಯ ಹೆಸರು",
        "phone": "ದೂರವಾಣಿ ಸಂಖ್ಯೆ",
        "address": "ವಿಳಾಸ",
        "category": "ವಿಭಾಗ",
        "amount": "ಮೊತ್ತ",
        "payment_mode": "ಪಾವತಿ ವಿಧಾನ",
        "cash": "ನಗದು",
        "upi": "UPI",
        "utr": "UTR ಸಂಖ್ಯೆ",
        "remarks": "ಟಿಪ್ಪಣಿ",
        "collected_by": "ಸಂಗ್ರಹಿಸಿದವರು",
        "thank_you": "ನಿಮ್ಮ ಉದಾರ ದೇಣಿಗೆಗಾಗಿ ಧನ್ಯವಾದಗಳು.",
        "signature": "ಅಧಿಕೃತ ಸಹಿ",
    },
    ReceiptLanguage.MR: {
        "title": "देणगी पावती",
        "receipt_no": "पावती क्रमांक",
        "date": "दिनांक",
        "donor_name": "देणगीदाराचे नाव",
        "phone": "दूरध्वनी क्रमांक",
        "address": "पत्ता",
        "category": "प्रकार",
        "amount": "रक्कम",
        "payment_mode": "देयक पद्धत",
        "cash": "रोख",
        "upi": "UPI",
        "utr": "UTR क्रमांक",
        "remarks": "शेरा",
        "collected_by": "संकलक",
        "thank_you": "आपल्या उदार देणगीबद्दल धन्यवाद.",
        "signature": "अधिकृत स्वाक्षरी",
    },
}


class ReceiptPDFService(BaseService):
    """Renders a ``Donation`` as a PDF receipt in the requested language."""

    @classmethod
    def generate(cls, donation: Donation, language: str | None = None) -> bytes:
        language = language or donation.receipt_language
        labels = RECEIPT_LABELS.get(language, RECEIPT_LABELS[ReceiptLanguage.EN])
        temple = TempleSettingsService.get_settings()

        context: dict[str, Any] = {
            "donation": donation,
            "labels": labels,
            "temple": temple,
        }
        html_string = render_to_string("receipts/receipt.html", context)
        return HTML(string=html_string).write_pdf()
