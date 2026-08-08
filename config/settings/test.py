"""Settings used by the automated test suite."""

from .base import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = "test-secret-key"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("TEST_DATABASE_NAME", default="ra_backend_test"),  # noqa: F405
        "USER": env("DATABASE_USER", default="ra_user"),  # noqa: F405
        "PASSWORD": env("DATABASE_PASSWORD", default="ra_password"),  # noqa: F405
        "HOST": env("DATABASE_HOST", default="localhost"),  # noqa: F405
        "PORT": env("DATABASE_PORT", default="5432"),  # noqa: F405
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_THROTTLE_RATES": {
        **REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"],  # type: ignore  # noqa: F405
        "anon": None,
        "user": None,
        "signup": None,
        "login": None,
    },
}
