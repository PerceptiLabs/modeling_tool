import os

CELERY = os.getenv("PL_KERNEL_CELERY")

# for now, use the same server
CELERY_REDIS_URL = os.getenv("PL_REDIS_URL")
CACHE_REDIS_URL = os.getenv("PL_REDIS_URL")
PUBSUB_REDIS_URL = os.getenv("PL_REDIS_URL")

TRAINING_PORT_MIN = os.getenv("TRAINING_PORT_MIN", 60000)
TRAINING_PORT_MAX = os.getenv("TRAINING_PORT_MAX", 65535)
TRAINING_DUMP_ROWS = os.getenv("PL_TRAINING_DUMP_ROWS")

TRAINING_RESULTS_REFRESH_INTERVAL = 3.0  # seconds [None == for every iteration]
TESTING_RESULTS_REFRESH_INTERVAL = None  # seconds [None == for every iteration]
SERVING_RESULTS_REFRESH_INTERVAL = 1.0  # seconds [None == for every iteration]
SERVING_MAX_TTL = 300  # seconds

RYGG_FILE_SERVING_TOKEN = os.getenv("PL_FILE_SERVING_TOKEN", "12312")
RYGG_BASE_URL = os.getenv("PL_RYGG_BASE_URL", "http://127.0.0.1:8000")


MIXPANEL_TOKEN_PROD = "1480b2244fdd4d821227a29e2637f922"  # TODO: should be env var..!
MIXPANEL_TOKEN_DEV = "8312db76002e43f8a9dc9acf9a12c1fc"  # TODO: should be env var..!

ENABLE_TF_GPU_MEMORY_GROWTH = os.getenv("ENABLE_TF_GPU_MEMORY_GROWTH", "False")

SENTRY_DSN = "https://94cbefca287f42cf9e800f20b7eb131b@o283802.ingest.sentry.io/6061749"  # Apparently this is safe to keep in public: https://docs.sentry.io/product/sentry-basics/dsn-explainer/#dsn-utilization
SENTRY_ENABLED_PROD = True
SENTRY_ENABLED_DEV = True
SENTRY_ENV_PROD = "prod"
SENTRY_ENV_DEV = "dev"

##### Will be edited by the build script #####
AUTH_ENV_DEFAULT = "dev"
##############################################
AUTH_ENV = os.getenv("AUTH_ENV", AUTH_ENV_DEFAULT)
if not AUTH_ENV:
    AUTH_ISSUER = None
elif AUTH_ENV == "dev":
    AUTH_ISSUER = "https://auth-dev.perceptilabs.com/"
    AUTH_AUDIENCE = "https://backends-dev.perceptilabs.com/"
elif AUTH_ENV == "prod":
    AUTH_ISSUER = os.getenv("AUTH_ISSUER", "https://auth.perceptilabs.com/")
    AUTH_AUDIENCE = os.getenv("AUTH_AUDIENCE", "https://backends.perceptilabs.com/")
else:
    raise Exception(
        f"AUTH_ENV is invalid. Got '{AUTH_ENV}'. Expected 'dev', 'prod' or empty string."
    )

AUTH_CERTS_URL = f"{AUTH_ISSUER}.well-known/jwks.json"
AUTH_ALGORITHM = "RS256"
