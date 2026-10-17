"""
Django settings for the Blood Bank Management System.

Works locally out of the box (SQLite, DEBUG on) and on Render / any host
when the environment variables below are provided:

    SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL,
    EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
"""
import os
import sys
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Core
# --------------------------------------------------------------------------
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-insecure-key-change-me')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('1', 'true', 'yes')

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.onrender.com']
ALLOWED_HOSTS += [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'blood',
    'donor',
    'patient',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bloodbankmanagement.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blood.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'bloodbankmanagement.wsgi.application'

# --------------------------------------------------------------------------
# Database  (SQLite locally, PostgreSQL on Render via DATABASE_URL)
# --------------------------------------------------------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Static & media
# --------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
_TESTING = 'test' in sys.argv
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        # hashed, compressed files in production; plain files while developing / testing
        'BACKEND': ('django.contrib.staticfiles.storage.StaticFilesStorage' if (DEBUG or _TESTING)
                    else 'whitenoise.storage.CompressedManifestStaticFilesStorage'),
    },
}
WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------
LOGIN_URL = '/adminlogin'
LOGIN_REDIRECT_URL = '/afterlogin'
LOGOUT_REDIRECT_URL = '/'

# --------------------------------------------------------------------------
# Blood bank business rules
# --------------------------------------------------------------------------
DONATION_GAP_DAYS = 90          # minimum days between two donations
DONOR_MIN_AGE = 18
DONOR_MAX_AGE = 65
LOW_STOCK_ML = 1000             # below this a blood group is flagged "Low"
CRITICAL_STOCK_ML = 400         # below this a blood group is flagged "Critical"
FULL_STOCK_ML = 5000            # used only to draw the stock level bars

# --------------------------------------------------------------------------
# Email (prints to the console unless real credentials are supplied)
# --------------------------------------------------------------------------
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_BACKEND = (
    'django.core.mail.backends.smtp.EmailBackend'
    if EMAIL_HOST_USER else 'django.core.mail.backends.console.EmailBackend'
)

# --------------------------------------------------------------------------
# Production security
# --------------------------------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
