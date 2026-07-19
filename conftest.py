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
def analyst_user(user_factory):
    return user_factory(user_type="ANALYST")


@pytest.fixture
def subscriber_user(user_factory):
    return user_factory(user_type="SUBSCRIBER")


@pytest.fixture
def authenticated_client(api_client, analyst_user):
    refresh = RefreshToken.for_user(analyst_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client, analyst_user
