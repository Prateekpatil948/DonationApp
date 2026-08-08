import factory
from factory.django import DjangoModelFactory

from apps.donations.models import Donation, DonationCategory
from core.constants.choices import PaymentMode, ReceiptLanguage


class DonationCategoryFactory(DjangoModelFactory):
    class Meta:
        model = DonationCategory
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Category {n}")
    is_active = True
    goal_amount = "10000.00"


class DonationFactory(DjangoModelFactory):
    class Meta:
        model = Donation

    donor_name = factory.Faker("name")
    category = factory.SubFactory(DonationCategoryFactory)
    amount = "100.00"
    payment_mode = PaymentMode.CASH
    receipt_language = ReceiptLanguage.EN
    receipt_number = factory.Sequence(lambda n: f"TDMS-{n:06d}")
    donation_date = factory.Faker("date_this_year")

    @factory.lazy_attribute
    def collected_by(self):
        from apps.users.tests.factories import UserFactory

        return UserFactory()
