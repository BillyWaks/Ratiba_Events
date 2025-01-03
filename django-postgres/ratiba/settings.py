"""
Django settings for ratiba project.

Generated by 'django-admin startproject' using Django 5.1.2.
For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
from decouple import config  # for env variable handling
import datetime
import environ
import os
import django_heroku
import dj_database_url
import logging
from pathlib import Path

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Media settings
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Quick-start development settings - unsuitable for production
SECRET_KEY = env("SECRET_KEY")


# The `DYNO` env var is set on Heroku CI, but it's not a real Heroku app, so we have to
# also explicitly exclude CI:
# https://devcenter.heroku.com/articles/heroku-ci#immutable-environment-variables
# IS_HEROKU_APP = "DYNO" in os.environ and not "CI" in os.environ

# # SECURITY WARNING: don't run with debug turned on in production!
# if not IS_HEROKU_APP:
#     DEBUG = True

# On Heroku, it's safe to use a wildcard for `ALLOWED_HOSTS``, since the Heroku router performs
# validation of the Host header in the incoming HTTP request. On other platforms you may need to
# list the expected hostnames explicitly in production to prevent HTTP Host header attacks. See:
# https://docs.djangoproject.com/en/5.1/ref/settings/#std-setting-ALLOWED_HOSTS
# if IS_HEROKU_APP:
#     ALLOWED_HOSTS = ["*"]
# else:
#     ALLOWED_HOSTS = [".localhost", "127.0.0.1", "[::1]", "0.0.0.0"]



# # Security settings
DEBUG = False 
# #env('DEBUG') #== 'False'  # Ensure this is set to 'False' in production
ALLOWED_HOSTS = ['djangoratiba.herokuapp.com', 'localhost', '127.0.0.1']
#     # '127.0.0.1',
#     # Add your domain name here if you have one
# # ]

AUTH_USER_MODEL = "authentication.User"

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'authentication',
    'base',
    'django_filters',
    'drf_yasg',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
]

# Swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Place CORS middleware at the top
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Add your custom token validation middleware
    'authentication.middleware.TokenValidationMiddleware',  # Ensure correct path
]


ROOT_URLCONF = 'ratiba.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        # 'DIRS': [BASE_DIR / 'templates'],  # Templates directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ratiba.wsgi.application'

# Determine if the app is running on Heroku
logger = logging.getLogger(__name__)

IS_HEROKU = os.environ.get('IS_HEROKU', 'False') == 'True' # Check for a unique Heroku environment variable

if IS_HEROKU:
    # Database settings for Heroku (PostgreSQL)
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('HEROKU_POSTGRESQL_ORANGE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }
    logger.info("Using Heroku PostgreSQL database settings.")
else:
    # Local database settings (PostgreSQL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': config("DB_NAME"),     # Load from environment
            'USER': config("DB_USER"),     # Load from environment
            'PASSWORD': config("DB_PASSWORD"),  # Load from environment
            'HOST': config("DB_HOST"),     # Load from environment
            'PORT': config("DB_PORT"),     # Load from environment
        }
    }
    logger.info("Using local PostgreSQL database settings.")
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': env("DB_NAME"),
#         'USER': env("DB_USER"),
#         'PASSWORD': env("DB_PASSWORD"),
#         'HOST': env("DB_HOST"),
#         'PORT': env("DB_PORT"),
#     }
# }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# REST framework settings
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
    'NON_FIELD_ERRORS_KEY': 'error',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',  # Change to AllowAny for all views, or adjust as needed
    ),
}


# Simple JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,  # Rotates refresh tokens on each use
    'BLACKLIST_AFTER_ROTATION': True,
}

# Internationalization/ Time zone settings
# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'  # Keep as UTC
# USE_I18N = True
# USE_L10N = True
# USE_TZ = True

# Localization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'  # Change to East Africa Time
USE_I18N = True
USE_L10N = True
USE_TZ = True

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_ROOT = BASE_DIR / 'staticfiles'  # For deployment
# Only if using WhiteNoise for serving static files
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# # Static files (CSS, JavaScript, images)
# STATIC_URL = '/static/'

# # Use the 'whitenoise' package for static file handling in production (recommended for Heroku)
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# # Add any custom static directories here if necessary
# STATICFILES_DIRS = [
#     BASE_DIR / "static",
# ]

# # Ensure you collect static files into the 'staticfiles' directory for Heroku
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_SSL = False
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# Additional security settings for production
# if not DEBUG:
#     SECURE_BROWSER_XSS_FILTER = True
#     SECURE_CONTENT_TYPE_NOSNIFF = True
#     SECURE_SSL_REDIRECT = True
#     SESSION_COOKIE_SECURE = True
#     CSRF_COOKIE_SECURE = True

# Heroku settings
# django_heroku.settings(locals(), databases=False)
django_heroku.settings(locals())