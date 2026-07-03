import os

from .base import *  # noqa: F401,F403

DEBUG = True

# "*" lets a physical device on the LAN reach `runserver 0.0.0.0:8000` during
# mobile development without hand-editing the host's IP here each time.
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# In development, allow any origin so a Flutter Web build / device can call the
# API. Native mobile builds don't send an Origin header, so this is only for
# convenience while developing the mobile client.
CORS_ALLOW_ALL_ORIGINS = True

if not os.environ.get("DB_NAME"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }
