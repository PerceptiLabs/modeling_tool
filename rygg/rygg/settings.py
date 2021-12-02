"""
Django settings for rygg project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import sys
import uuid
from pathlib import Path
import sentry_sdk
from rygg import __version__    
from sentry_sdk.integrations.django import DjangoIntegration

def is_prod():
    return __version__ != "development"

# According to Sentry, DSNs are safe to keep public
# https://docs.sentry.io/product/sentry-basics/dsn-explainer/
SENTRY_DSN = "https://56aaa2a9837147f9bd8778a9f4c6f878@o283802.ingest.sentry.io/6061756"  

if is_prod():
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        send_default_pii=True,
        release=__version__
    )


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

def is_docker():
    try:
        return os.path.isfile("/.dockerenv")
    except:
        return False

def is_podman():
    # see https://github.com/containers/podman/issues/3586
    # in podman, the "container" variable is set
    return os.getenv("container") is not None

IS_CONTAINERIZED = is_docker() or is_podman()

DB_LOCATION = os.environ.get("PERCEPTILABS_DB")
if DB_LOCATION or not IS_CONTAINERIZED:
    DB_LOCATION = os.environ.get("PERCEPTILABS_DB") or os.path.join(Path.home(), ".perceptilabs/db.sqlite3")
    db_dir=os.path.dirname(DB_LOCATION)
    os.makedirs(db_dir, exist_ok=True)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-nj5*1agd@#(1*gcm2kd2q!*ui!kg2*yew=ata$n!sj-nnl&a7'

ALLOWED_HOSTS = ['*'] if IS_CONTAINERIZED else ["localhost", "127.0.0.1"]

APPEND_SLASH=True

# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rygg.api',
    'rygg.files',
    'rygg.mixpanel_proxy',
    "django_extensions",
]

MIDDLEWARE = [
    "request_logging.middleware.LoggingMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_http_exceptions.middleware.ExceptionHandlerMiddleware",
    "django_http_exceptions.middleware.ThreadLocalRequestMiddleware",
    "rygg.middleware.token_middleware",
]

ROOT_URLCONF = 'rygg.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'rygg.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_LOCATION,
    },
    'postgres': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASS'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

default_database = os.getenv('DJANGO_DATABASE', 'default')
DATABASES['default'] = DATABASES[default_database]

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

REST_FRAMEWORK = {
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 10
        }

# CORS_ALLOW_CREDENTIALS and CORS_ORIGIN_WHITELIST are set to more restrictive values for MixPanel's sake
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = IS_CONTAINERIZED

if not IS_CONTAINERIZED:
    CORS_ORIGIN_WHITELIST = [os.environ.get('FRONTEND_BASE_URL', 'http://localhost:8080')]

LOGGING = {
    'version': 1,
    "disable_existing_loggers": False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        "django.request": {
            "handlers": ["console"],
            'level': os.getenv('PL_RYGG_LOG_LEVEL', 'WARNING'),
            "propagate": False,
        },
        'django.db.backends': {
            "handlers": ["console"],
            'level': os.getenv('PL_RYGG_LOG_LEVEL', 'WARNING'),
        },
        'rygg': {
            'handlers': ['console'],
            'level': os.getenv('RYGG_LOG_LEVEL', 'WARNING'),
        },
    },
}

# Github
GITHUB_API_KEY = os.environ.get('GITHUB_API_KEY', '')
GITHUB_API_ENDPOINT = os.environ.get('GITHUB_API_ENDPOINT', '')

# Endpoint to fetch current machine's external IP address
EXTERNAL_IP_RESOLVER_ENDPOINT = 'https://api.ipify.org'

IS_SERVING = "runserver" in sys.argv
IS_WORKER = "celery" in " ".join(sys.argv)

# Enforcement of the token
API_TOKEN = os.getenv("PL_FILE_SERVING_TOKEN")
API_TOKEN_REQUIRED = not DEBUG and not IS_CONTAINERIZED and IS_SERVING

if API_TOKEN_REQUIRED and not API_TOKEN:
    raise Exception("The PL_FILE_SERVING_TOKEN environment variable hasn't been set")

def assert_dir_writable(dir, msg):
    test_file = os.path.join(dir, "test_writable_file" + str(uuid.uuid1()))
    try:
        open(test_file, "a").close()
    except:
        raise Exception(msg)

    os.remove(test_file)

# Make sure BASE_UPLOAD_DIR is set
BASE_UPLOAD_DIR=None
if IS_CONTAINERIZED and (IS_SERVING or IS_WORKER):
    BASE_UPLOAD_DIR = os.path.abspath(os.getenv("PL_FILE_UPLOAD_DIR"))
    if not BASE_UPLOAD_DIR:
        raise Exception("Required environment variable PL_FILE_UPLOAD_DIR is not set.")

    if not os.path.isdir(BASE_UPLOAD_DIR):
        raise Exception(f"PL_FILE_UPLOAD_DIR is set to '{BASE_UPLOAD_DIR}' but that directory doesn't exist")

    assert_dir_writable(BASE_UPLOAD_DIR, f"PL_FILE_UPLOAD_DIR is set to '{dir}' but that directory isn't writable")

def is_upload_allowed():
    return not not BASE_UPLOAD_DIR

def file_upload_dir(project_id):
    if not BASE_UPLOAD_DIR:
        raise Exception("PL_FILE_UPLOAD_DIR hasn't been set")
    if not os.path.isdir(BASE_UPLOAD_DIR):
        raise FileNotFoundError(BASE_UPLOAD_DIR)

    return os.path.join(BASE_UPLOAD_DIR, str(project_id))


FILE_UPLOAD_HANDLERS = [
    # story 1588: turn off in-memory uploads
    # 'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

FILE_UPLOAD_PERMISSIONS = 0o444
# since we're accepting uploads from large files, turn off the check for upload size
DATA_UPLOAD_MAX_MEMORY_SIZE = None

CELERY_BROKER_URL = os.environ.get("PL_REDIS_URL", "redis://127.0.0.1:6379")
CELERY_RESULT_BACKEND = os.environ.get("PL_REDIS_URL", "redis://127.0.0.1:6379")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_ENABLED = True

# Azure blob
DATA_BLOB = os.getenv('PL_DATA_BLOB', "https://perceptilabs.blob.core.windows.net/data")
DATA_LIST = os.getenv('PL_DATA_LIST', DATA_BLOB + "/dataset-list.csv")
DATA_CATEGORY_LIST = os.getenv('PL_DATA_CATEGORY_LIST', DATA_BLOB + "/dataset-categories.csv")

DEFAULT_PROJECT_NAME = "Default"
DEFAULT_PROJECT_DIR = os.path.join(Path.home(), 'Documents', 'Perceptilabs', 'Default')

