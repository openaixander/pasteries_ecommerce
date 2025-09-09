"""
Django settings for dee_pastery project.
"""

import os
from pathlib import Path
from django.contrib.messages import constants as messages
from decouple import config, Csv
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------
# SECURITY
# -------------------
SECRET_KEY = config("SECRET_KEY", default="insecure-dev-key")
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
    cast=Csv()
)

# -------------------
# APPLICATIONS
# -------------------
INSTALLED_APPS = [
    'accounts',
    'carts',
    'logo',
    'store',
    'orders',

    # third-party
    'jazzmin',
    'cloudinary',
    'paystack',

    # django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dee_pastery.urls'
AUTH_USER_MODEL = 'accounts.Account'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.menu_links',
                'carts.context_processors.counter',
            ],
        },
    },
]

WSGI_APPLICATION = 'dee_pastery.wsgi.application'

# -------------------
# DATABASE
# -------------------
if config("DATABASE_URL", default=None):
    DATABASES = {
        "default": dj_database_url.config(
            default=config("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=False
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
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
# INTERNATIONALIZATION
# -------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------
# STATIC & MEDIA
# -------------------
STATIC_URL = "/static/"
MEDIA_URL = "/images/"

MEDIA_ROOT = BASE_DIR / "media/images"

if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------
# DEFAULT PRIMARY KEY
# -------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------
# MESSAGES
# -------------------
MESSAGE_TAGS = {
    messages.ERROR: "danger",
}

# -------------------
# AUTH / LOGIN
# -------------------
LOGIN_URL = "accounts:login"

SESSION_EXPIRE_SECONDS = 3600
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True

# -------------------
# EMAIL
# -------------------
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = True

# -------------------
# PAYSTACK
# -------------------
PAYSTACK_SECRET_KEY = config("PAYSTACK_SECRET_KEY", default="")
PAYSTACK_PUBLIC_KEY = config("PAYSTACK_PUBLIC_KEY", default="")

# -------------------
# JAZZMIN
# -------------------
SITE_TITLE = "Shishicakes Admin"
JAZZMIN_SETTINGS = {
    "site_brand": "ShiShiCakes",
    "welcome_sign": "Welcome ShiShiCakes",
    "copyright": "ShiShiCakes",
    "login_logo": None,
    "site_icon": "../static/tie-690084__480_32x32.jpg",
    "site_logo_classes": "img-circle",
}

# -------------------
# CLOUDINARY
# -------------------
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUD_NAME", default=""),
    "CLOUD_API_KEY": config("API_KEY", default=""),
    "CLOUD_API_SECRET": config("API_SECRET", default=""),
}

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE["CLOUD_NAME"],
    api_key=CLOUDINARY_STORAGE["CLOUD_API_KEY"],
    api_secret=CLOUDINARY_STORAGE["CLOUD_API_SECRET"],
)
