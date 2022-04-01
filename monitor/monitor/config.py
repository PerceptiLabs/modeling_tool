import os
import yaml


def load_config():
    if not os.path.isfile("queues.yaml"):
        raise Exception("Didn't find queues.yaml.")

    with open("queues.yaml", "r") as f:
        return yaml.safe_load(f)
