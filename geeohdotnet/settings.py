"""
Django settings for geeohdotnet project.
"""
import json

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

with open('credentials.json', 'r') as f:
    credentials = json.loads(f.read())

SECRET_KEY = credentials['secret_key']

DEBUG = credentials['debug']

ALLOWED_HOSTS = ['localhost', 'geeoh.net']

# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'geeohdotnet',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

AUTH_USER_MODEL = 'geeohdotnet.User'

AUTHENTICATION_BACKENDS = [
    'geeohdotnet.backends.AuthBackend',
]

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
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = 'media/'
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600
