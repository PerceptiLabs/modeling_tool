from monitor.celery_wrap import all_tasks
from monitor.k8s_scale import scale_deployments
from monitor.predictions import get_predictions
from monitor.settings import CONFIG
import logging
import sys


if __name__ == "__main__":
    logging.info(CONFIG)
    tasks = all_tasks()
    scales = get_predictions(tasks)
    if "--dry-run" not in sys.argv:
        scale_deployments(scales)
