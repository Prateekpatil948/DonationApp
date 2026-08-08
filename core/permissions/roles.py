"""Role-based DRF permission classes.

TDMS has two roles - Admin and Member - each of which must additionally be
in ``ACTIVE`` status (``MemberStatus``) to use the API at all.
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from core.constants.choices import MemberStatus, UserRole


class IsAdminRole(BasePermission):
    """Allow access only to authenticated users with the ADMIN role."""

    message = "This action is restricted to temple administrators."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return getattr(user, "role", None) == UserRole.ADMIN


class IsActiveMember(BasePermission):
    """Allow access to any authenticated Admin/Member whose status is ACTIVE."""

    message = "Your account is not active."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return getattr(user, "status", None) == MemberStatus.ACTIVE
