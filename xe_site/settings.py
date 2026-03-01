"""
Django settings for xe_site project.
Production-ready configuration
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# -------------------
# BASE
# -------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# -------------------
# SECURITY
# -------------------
SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = [
    host for host in os.getenv("ALLOWED_HOSTS", "").split(",") if host
]

CSRF_TRUSTED_ORIGINS = [
    origin for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if origin
]

# -------------------
# OPENAI
# -------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# -------------------
# AUTH
# -------------------
LOGIN_REDIRECT_URL = "profile"
LOGOUT_REDIRECT_URL = "home"
LOGIN_URL = "login"

# -------------------
# APPS
# -------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "main",
    "accounts",

    "django_ckeditor_5",
    "django.contrib.sitemaps",
]

# -------------------
# MIDDLEWARE
# -------------------
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

# -------------------
# URLS / WSGI
# -------------------
ROOT_URLCONF = "xe_site.urls"
WSGI_APPLICATION = "xe_site.wsgi.application"

# -------------------
# TEMPLATES
# -------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# -------------------
# DATABASE
# -------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'xediaryby_xe_db',
        'USER': 'xediaryby_xe_user',
        'PASSWORD': 'pacavaca22',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# -------------------
# PASSWORDS
# -------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------
# I18N
# -------------------
LANGUAGE_CODE = "ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

# -------------------
# STATIC
# -------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------
# MEDIA
# -------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -------------------
# AUTH USER
# -------------------
AUTH_USER_MODEL = "accounts.CustomUser"

# -------------------
# CKEDITOR
# -------------------
CKEDITOR_5_CUSTOM_CSS = "ckeditor5/custom.css"

CKEDITOR_5_CONFIGS = {
    "default": {
        "extends": None,
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "|",
            "outdent",
            "indent",
            "|",
            "blockQuote",
            "insertTable",
            "imageUpload",
            "|",
            "undo",
            "redo",
        ],
        "language": "ru",
    },
}

CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
CKEDITOR_5_UPLOAD_PLUGIN = "image"

# -------------------
# DEFAULT PK
# -------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# -------------------
# SECURITY (PRODUCTION)
# -------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = False
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False