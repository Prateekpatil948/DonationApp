"""Shared base class for the service layer.

App-specific services (``apps.users.services.UserService``,
``apps.authentication.services.GoogleAuthService``, etc.) subclass this so
views never touch the ORM directly - see the Service Layer Pattern section
of the TRD.
"""


class BaseService:
    """Marker base class for service-layer objects."""
