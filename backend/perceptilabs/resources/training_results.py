import base64
import time
import platform
import pickle
import os
import logging
from retrying import retry


from perceptilabs.utils import directory_tree


from filelock import FileLock


logger = logging.getLogger(__name__)


class ModelDirectoryCorrupt(Exception):
    pass


class TrainingResultsAccess:
    FILE_NAME = "latest-training-results.pkl"

    def __init__(self, rygg):
        self._rygg = rygg

    def store(self, call_context, training_session_id, results):
        if training_session_id is None:
            return None

        path = self._get_path(call_context, training_session_id)
        with FileLock(path + ".lock"):
            with open(path, "wb") as f:
                pickle.dump(results, f)
                size = os.path.getsize(path)
                logger.info(f"Size of latest training results in bytes: {size}")

    def get_latest(self, call_context, training_session_id):
        if training_session_id is None:
            return None

        path = self._get_path(call_context, training_session_id)
        if not os.path.isfile(path):
            self._print_missing_file_error(path, training_session_id)
            return None

        results_dict = {}
        with FileLock(path + ".lock"):
            with open(path, "rb") as f:
                results_dict = pickle.load(f)

        if not results_dict:
            logger.error(
                f"Invalid training results for training session id {training_session_id}. No content found."
            )
            return None

        return results_dict

    def _print_missing_file_error(self, path, training_session_id):
        error_message = f"Invalid training results path: {path} for training session id {training_session_id}"

        modeldir = os.path.dirname(path)
        if os.path.isdir(modeldir):
            error_message += ". Directory tree:\n"
            for found_path in directory_tree(modeldir):
                error_message += "  " + found_path + "\n"

        logger.error(error_message)

    def _get_path(self, call_context, training_session_id):
        model_dir = self._rygg.get_model(call_context, training_session_id)["location"]
        model_dir = model_dir.replace("\\", "/")  # Sanitize Windows path

        ckpt_dir = os.path.join(model_dir, "checkpoint")

        if os.path.isfile(ckpt_dir):
            raise ModelDirectoryCorrupt(
                f"Creating checkpoint directory failed because a file with the same path already exists. Path: {ckpt_dir}"
            )

        os.makedirs(ckpt_dir, exist_ok=True)
        file_path = os.path.join(ckpt_dir, self.FILE_NAME)
        return file_path

    def remove(self, call_context, training_session_id):
        @retry(
            stop_max_attempt_number=3, wait_fixed=500
        )  # Windows needs several attempts
        def do_remove(path):
            if os.path.isfile(path):
                with FileLock(path + ".lock"):
                    os.remove(path)

        if training_session_id is not None:
            path = self._get_path(call_context, training_session_id)
            do_remove(path)
