from monitor.celery_wrap import all_tasks
from monitor.k8s_scale import scale_deployments
from monitor.predictions import Predictor
from monitor.settings import CONFIG
import logging
import sys


if __name__ == "__main__":
    predictor = Predictor(CONFIG)
    logging.info(CONFIG.as_dict)

    tasks = all_tasks()
    scales = predictor.get_predictions(tasks)
    if "--dry-run" not in sys.argv:
        scale_deployments(scales)
