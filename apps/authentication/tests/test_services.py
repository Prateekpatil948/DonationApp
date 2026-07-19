from unittest.mock import patch

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.services import GoogleAuthService, TokenService
from core.exceptions.exceptions import InvalidGoogleTokenError, ServiceError

pytestmark = pytest.mark.django_db


@patch("apps.authentication.services.google_id_token.verify_oauth2_token")
def test_verify_id_token_raises_on_invalid_token(mock_verify):
    mock_verify.side_effect = ValueError("bad token")

    with pytest.raises(InvalidGoogleTokenError):
        GoogleAuthService.verify_id_token("bad-token")


@patch("apps.authentication.services.google_id_token.verify_oauth2_token")
def test_verify_id_token_rejects_unverified_email(mock_verify):
    mock_verify.return_value = {"sub": "1", "email": "x@example.com", "email_verified": False}

    with pytest.raises(InvalidGoogleTokenError):
        GoogleAuthService.verify_id_token("token")


def test_issue_tokens_for_user_returns_access_and_refresh(user_factory):
    user = user_factory()
    tokens = TokenService.issue_tokens_for_user(user)

    assert set(tokens.keys()) == {"access", "refresh"}


def test_blacklist_token_rejects_garbage_token():
    with pytest.raises(ServiceError):
        TokenService.blacklist_token("not-a-real-token")


def test_refresh_access_token_returns_new_access(user_factory):
    user = user_factory()
    refresh = RefreshToken.for_user(user)

    result = TokenService.refresh_access_token(str(refresh))

    assert "access" in result
