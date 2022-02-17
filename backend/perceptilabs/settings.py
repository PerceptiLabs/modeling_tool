import os

CELERY = os.getenv("PL_KERNEL_CELERY")

# for now, use the same server
CELERY_REDIS_URL = os.getenv("PL_REDIS_URL")
CACHE_REDIS_URL = os.getenv("PL_REDIS_URL")
PUBSUB_REDIS_URL = os.getenv("PL_REDIS_URL")

TRAINING_PORT_MIN = os.getenv("TRAINING_PORT_MIN", 60000)
TRAINING_PORT_MAX = os.getenv("TRAINING_PORT_MAX", 65535)
TRAINING_DUMP_ROWS = os.getenv("PL_TRAINING_DUMP_ROWS")

TRAINING_RESULTS_REFRESH_INTERVAL = 3.0 # seconds [None == for every iteration]
TESTING_RESULTS_REFRESH_INTERVAL = None # seconds [None == for every iteration]
SERVING_RESULTS_REFRESH_INTERVAL = 1.0 # seconds [None == for every iteration]


RYGG_FILE_SERVING_TOKEN = os.getenv("PL_FILE_SERVING_TOKEN", "12312")
RYGG_BASE_URL = os.getenv("PL_RYGG_BASE_URL", "http://127.0.0.1:8000")


MIXPANEL_TOKEN_PROD = '1480b2244fdd4d821227a29e2637f922'  # TODO: should be env var..!
MIXPANEL_TOKEN_DEV = '8312db76002e43f8a9dc9acf9a12c1fc'  # TODO: should be env var..!



SENTRY_DSN = "https://94cbefca287f42cf9e800f20b7eb131b@o283802.ingest.sentry.io/6061749"  # Apparently this is safe to keep in public: https://docs.sentry.io/product/sentry-basics/dsn-explainer/#dsn-utilization
SENTRY_ENABLED_PROD = True
SENTRY_ENABLED_DEV = True
SENTRY_ENV_PROD = "prod"
SENTRY_ENV_DEV = "dev"

##### Will be edited by the build script #####
AUTH_ENV_DEFAULT = 'dev'
##############################################
AUTH_ENV = os.getenv('AUTH_ENV', AUTH_ENV_DEFAULT)
if not AUTH_ENV:
    AUTH_ISSUER = None
elif AUTH_ENV == 'dev':
    AUTH_REALM = 'vue-perceptilabs'
    AUTH_ISSUER = f"https://keycloak.dev.perceptilabs.com:8443/auth/realms/{AUTH_REALM}"
    AUTH_CERTS_URL = f"{AUTH_ISSUER}/protocol/openid-connect/certs"
    AUTH_AUDIENCE = 'account'
    AUTH_ALGORITHM = 'RS256'
elif AUTH_ENV == 'prod':
    AUTH_REALM = os.getenv('AUTH_REALM', 'PerceptiLabs')
    AUTH_ISSUER = os.getenv('AUTH_ISSUER', f"https://keycloak.perceptilabs.com:8443/auth/realms/{AUTH_REALM}")
    AUTH_CERTS_URL = os.getenv('AUTH_CERTS_URL', f"{AUTH_ISSUER}/protocol/openid-connect/certs")
    AUTH_AUDIENCE = os.getenv('AUTH_AUDIENCE', 'account')
    AUTH_ALGORITHM = os.getenv('AUTH_ALGORITHM', 'RS256')
else:
    raise Exception(f"AUTH_ENV is invalid. Got '{AUTH_ENV}'. Expected 'dev', 'prod' or empty string.")
