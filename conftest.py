"""Shared pytest fixtures available to every test in the project."""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user_factory(db):
    from apps.users.tests.factories import UserFactory

    return UserFactory


@pytest.fixture
def admin_user(user_factory):
    from core.constants.choices import MemberStatus, UserRole

    return user_factory(role=UserRole.ADMIN, status=MemberStatus.ACTIVE, is_staff=True)


@pytest.fixture
def member_user(user_factory):
    from core.constants.choices import MemberStatus, UserRole

    return user_factory(role=UserRole.MEMBER, status=MemberStatus.ACTIVE)


@pytest.fixture
def authenticated_client(api_client, member_user):
    refresh = RefreshToken.for_user(member_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client, member_user


@pytest.fixture
def admin_client(api_client, admin_user):
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client, admin_user


@pytest.fixture
def temple_settings(db):
    from apps.common.models import TempleSettings

    return TempleSettings.objects.create(temple_name="Sri Test Temple")


@pytest.fixture
def category_factory(db):
    from apps.donations.tests.factories import DonationCategoryFactory

    return DonationCategoryFactory


@pytest.fixture
def donation_factory(db):
    from apps.donations.tests.factories import DonationFactory

    return DonationFactory
