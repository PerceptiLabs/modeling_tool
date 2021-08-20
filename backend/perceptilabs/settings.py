import os

CELERY = os.getenv("PL_KERNEL_CELERY", False)

# for now, use the same server
CELERY_REDIS_URL = os.getenv("PL_REDIS_URL", None)
CACHE_REDIS_URL=os.getenv("PL_REDIS_URL", None)

TRAINING_PORT_MIN = os.getenv("TRAINING_PORT_MIN", 60000)
TRAINING_PORT_MAX = os.getenv("TRAINING_PORT_MAX", 65535)

