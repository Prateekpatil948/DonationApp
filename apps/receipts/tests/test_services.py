import pytest

from apps.receipts.services import ReceiptPDFService

pytestmark = pytest.mark.django_db


def test_generate_pdf_returns_non_empty_bytes(donation_factory, temple_settings):
    donation = donation_factory()
    pdf_bytes = ReceiptPDFService.generate(donation)

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")


@pytest.mark.parametrize("language", ["EN", "KN", "MR"])
def test_generate_pdf_supports_all_languages(donation_factory, temple_settings, language):
    donation = donation_factory(receipt_language=language)
    pdf_bytes = ReceiptPDFService.generate(donation)

    assert pdf_bytes.startswith(b"%PDF")


def test_generate_pdf_language_override(donation_factory, temple_settings):
    donation = donation_factory(receipt_language="EN")
    pdf_bytes = ReceiptPDFService.generate(donation, language="KN")

    assert pdf_bytes.startswith(b"%PDF")
