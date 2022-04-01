import os
from monitor.config import load_config

LOG_LEVEL = os.getenv("PL_MONITOR_LOG_LEVEL", "WARNING")
REDIS_URL = os.getenv("PL_REDIS_URL", "redis://localhost:6379")
CONFIG = load_config()
