import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv


import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# Set these as environment variables in production.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me-before-going-live")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".vercel.app"]
CSRF_TRUSTED_ORIGINS = ["https://*.vercel.app"]

# nviron.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h] + [".vercel.app"]
# CSRF_TRUSTED_ORIGINS = [o for o in os.environ.get("DJANGO_CSRF_ORIGINS", "").split(",") if o] + ["https://*.vercel.app"]ALLOWED_HOSTS = [h for h in os.e

# Public address of the site, used inside the table QR codes (for example https://williams.example.com).
# Leave empty to use whatever address the owner is browsing from.
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "restaurant",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "williams.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "restaurant.context_processors.shop",
    ]},
}]

WSGI_APPLICATION = "williams.wsgi.application"

# Database: Neon (PostgreSQL) when DATABASE_URL is set, otherwise SQLite on your own computer.
# Vercel's disk is read-only, so SQLite cannot work there.
# DATABASE_URL = os.environ.get("DATABASE_URL", "")
# if os.environ.get("VERCEL") and not DATABASE_URL:
#     raise ImproperlyConfigured(
#         "DATABASE_URL is not set. In Vercel open Settings > Environment Variables, add DATABASE_URL "
#         "with your Neon connection string, then redeploy."
#     )
    
# DATABASES = {"default": dj_database_url.config(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}", conn_max_age=600)}

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=0,           # serverless: close the connection after each request
        conn_health_checks=True,  # check a connection is alive before reusing it
        ssl_require=True,         # Neon only accepts encrypted (SSL) connections
    )
}

DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True

# DATABASES = {
#     "default": dj_database_url.config(
#         default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
#         conn_max_age=0,
#     )
# # }
# if DATABASES["default"]["ENGINE"].endswith("postgresql"):
#     DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True  # needed with Neon's pooled connection

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 6}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

LANGUAGE_CODE = "en"
TIME_ZONE = "Asia/Kuala_Lumpur"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
WHITENOISE_USE_FINDERS = True  # serve CSS straight from the app, even if collectstatic was not run
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "menu"
LOGOUT_REDIRECT_URL = "menu"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
