"""Role-based DRF permission classes.

The PRD calls for Anonymous, Authenticated, Admin, Analyst and Subscriber
permission tiers. ``IsAuthenticated``/``AllowAny`` (DRF built-ins) cover the
first two; these classes cover the role-specific ones.
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from core.constants.choices import UserType


class IsAnalyst(BasePermission):
    """Allow access only to authenticated users with the ANALYST role."""

    message = "This action is restricted to analyst accounts."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return getattr(user, "user_type", None) == UserType.ANALYST


class IsSubscriber(BasePermission):
    """Allow access only to authenticated users with the SUBSCRIBER role."""

    message = "This action is restricted to subscriber accounts."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return getattr(user, "user_type", None) == UserType.SUBSCRIBER


class IsAdminRole(BasePermission):
    """Allow access only to Django staff/superuser accounts."""

    message = "This action is restricted to administrators."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.is_staff)
