from unittest.mock import patch

import pytest

from apps.notifications.services import NotificationService

pytestmark = pytest.mark.django_db


def test_send_logs_notification_without_raising(user_factory):
    user = user_factory()

    with patch("apps.notifications.services.logger") as mock_logger:
        NotificationService.send(user, title="Welcome", message="Hello!")

    mock_logger.info.assert_called_once()
    assert mock_logger.info.call_args.args[0] == "notification_dispatched"
