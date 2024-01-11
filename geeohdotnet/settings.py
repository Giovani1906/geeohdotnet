"""
Django settings for geeohdotnet project.
"""
import json

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

with open('settings.json', 'rb') as f:
    settings = json.loads(f.read())

SECRET_KEY = settings['secret_key']

DEBUG = settings['debug']

ALLOWED_HOSTS = ['localhost', 'geeoh.net']

# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'axes',
    'geeohdotnet',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

AUTH_USER_MODEL = 'geeohdotnet.User'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'geeohdotnet.backends.AuthBackend',
]

AXES_ENABLED = True
AXES_FAILURE_LIMIT = 3
AXES_LOCK_OUT_AT_FAILURE = True
AXES_COOLOFF_TIME = 24
AXES_HANDLER = 'axes.handlers.cache.AxesCacheHandler'
AXES_LOCKOUT_TEMPLATE = 'ratelimit.html'
AXES_VERBOSE = DEBUG
AXES_IPWARE_PROXY_COUNT = 1
AXES_IPWARE_META_PRECEDENCE_ORDER = [
    'HTTP_X_REAL_IP',
    'HTTP_X_FORWARDED_FOR',
    'REMOTE_ADDR',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211' if not DEBUG else '192.168.1.128:11211',
    }
}

ROOT_URLCONF = 'geeohdotnet.urls'

LOGIN_URL = '/auth'

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
            ],
        },
    },
]

# Database

DATABASES = {}

# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = 'media/'
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600
