#!/usr/bin/env python

DESCRIPTION = """
For running celery workers in docker. It expects a config file named queues.yaml to be in the same directory

"""

import os
import subprocess
import yaml


def get_queue_configs(config, worker_type):
    def as_list():
        for queue_name, queue_config in config["queues"].items():
            for task_name, task_config in queue_config["tasks"].items():
                if task_config["worker_type"] == worker_type:
                    yield queue_name

    return list(set(as_list()))


def load_config(config_file):
    if not os.path.isfile(config_file):
        print(f"Missing required {config_file} file")
        exit(1)

    with open(config_file, "r") as f:
        return yaml.safe_load(f)


def main(worker_type, config_file, extras):
    config = load_config(config_file)
    worker_types = config["worker_types"]
    worker_config = worker_types.get(worker_type)
    if not worker_config:
        msg = f"ERROR: worker type {worker_type} isn't in the config file. Available: {', '.join(worker_types.keys())}"
        print(msg)
        exit(1)

    queues = get_queue_configs(config, worker_type)
    queues_str = ",".join(queues)
    concurrency = worker_config.get("concurrency", None)

    cmd = [
        "python",
        "-m",
        "celery",
        "--app=" + worker_config["class"],
        "worker",
        "--queues=" + queues_str,
        "--pool=threads",
        *extras,
    ]
    if concurrency:
        cmd.append(f"--concurrency={concurrency}")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            f"{DESCRIPTION}USAGE: {sys.argv[0]} <queue name> [-- ...args passed through to the kernel...]"
        )
        exit(1)

    WORKER_TYPE = sys.argv[1]

    def extras():
        found = False
        for arg in sys.argv[2:]:
            if found:
                yield arg

            if arg == "--":
                found = True

    main(WORKER_TYPE, "queues.yaml", list(extras()))
