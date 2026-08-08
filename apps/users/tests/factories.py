import factory
from factory.django import DjangoModelFactory

from apps.users.models import User
from core.constants.choices import MemberStatus, UserRole


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("phone_number",)

    phone_number = factory.Sequence(lambda n: f"+9190000{n:05d}")
    name = factory.Faker("name")
    role = UserRole.MEMBER
    status = MemberStatus.ACTIVE
    is_active = True

    @factory.post_generation
    def pin(self, create, extracted, **kwargs):
        if not create:
            return
        self.set_password(extracted or "123456")
        self.save(update_fields=["password"])
