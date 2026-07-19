import factory
from factory.django import DjangoModelFactory

from apps.users.models import User
from core.constants.choices import UserType


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.Sequence(lambda n: f"+91900000{n:04d}")
    user_type = UserType.ANALYST
    google_id = factory.Sequence(lambda n: f"google-id-{n}")
    is_verified = True
    is_active = True
