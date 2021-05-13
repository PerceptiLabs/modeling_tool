from pathlib import Path
import os
import sys
import uuid

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "%6c1c))#ez&wg+dh1nu_g-28xvoky4slq6j^y@9$*l)0i2b^+c"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

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
ALLOWED_HOSTS = ['*'] if IS_CONTAINERIZED else ["localhost", "127.0.0.1"]

# Enforcement of the token
API_TOKEN = os.getenv("PL_FILE_SERVING_TOKEN")
API_TOKEN_REQUIRED = not DEBUG and not IS_CONTAINERIZED and not "test" in sys.argv
if API_TOKEN_REQUIRED and not API_TOKEN:
    raise Exception("The PL_FILE_SERVING_TOKEN environment variable hasn't been set")

def assert_dir_writable(dir, msg):
    test_file = os.path.join(dir, "test_writable_file" + str(uuid.uuid1()))
    try:
        open(test_file, "a").close()
    except:
        raise Exception(msg)

    os.remove(test_file)

# Make sure FILE_UPLOAD_DIR is set
FILE_UPLOAD_DIR=None
if IS_CONTAINERIZED:
    FILE_UPLOAD_DIR = os.getenv("PL_FILE_UPLOAD_DIR")
    if not FILE_UPLOAD_DIR:
        raise Exception("Required environment variable PL_FILE_UPLOAD_DIR is not set.")

    if not os.path.isdir(FILE_UPLOAD_DIR):
        raise Exception(f"PL_FILE_UPLOAD_DIR is set to '{FILE_UPLOAD_DIR}' but that directory doesn't exist")

    assert_dir_writable(FILE_UPLOAD_DIR, f"PL_FILE_UPLOAD_DIR is set to '{dir}' but that directory isn't writable")


FILE_UPLOAD_HANDLERS = [
    # story 1588: turn off in-memory uploads
    # 'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

FILE_UPLOAD_PERMISSIONS = 0o444

INSTALLED_APPS = [
    "corsheaders",
    "fileserver.api",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    # "request_logging.middleware.LoggingMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_http_exceptions.middleware.ExceptionHandlerMiddleware",
    "django_http_exceptions.middleware.ThreadLocalRequestMiddleware",
    "fileserver.middleware.token_middleware",
]

ROOT_URLCONF = "fileserver.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "fileserver.wsgi.application"


# django.test insists on a db, so give it a disposable sqlite db
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"

# CORS_ALLOW_CREDENTIALS and CORS_ORIGIN_WHITELIST are set to more restrictive values for MixPanel's sake
CORS_ALLOW_CREDENTIALS = False
CORS_ORIGIN_ALLOW_ALL = IS_CONTAINERIZED

if not IS_CONTAINERIZED:
    CORS_ORIGIN_WHITELIST = [ 'http://localhost:8080', ]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler",},},
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            'level': os.getenv('PL_FILESERVER_LOG_LEVEL', 'WARNING'),
            "propagate": False,
        },
    },
}
