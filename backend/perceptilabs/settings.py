import os

CELERY = os.getenv("PL_KERNEL_CELERY")

# for now, use the same server
CELERY_REDIS_URL = os.getenv("PL_REDIS_URL")
CACHE_REDIS_URL = os.getenv("PL_REDIS_URL")

TRAINING_PORT_MIN = os.getenv("TRAINING_PORT_MIN", 60000)
TRAINING_PORT_MAX = os.getenv("TRAINING_PORT_MAX", 65535)

TRAINING_DUMP_ROWS = os.getenv("PL_TRAINING_DUMP_ROWS")
