"""Notification dispatch service, named in the TRD's Service Layer Pattern.

No delivery channel (push/email/SMS) is wired up yet - this is the seam
future apps call into once one is chosen.
"""

import logging

from apps.users.models import User
from services.base import BaseService

logger = logging.getLogger(__name__)


class NotificationService(BaseService):
    """Placeholder dispatcher for user-facing notifications."""

    @staticmethod
    def send(user: User, title: str, message: str) -> None:
        logger.info(
            "notification_dispatched",
            extra={"user_id": str(user.id), "title": title},
        )
