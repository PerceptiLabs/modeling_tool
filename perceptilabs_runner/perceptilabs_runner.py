import argparse
import importlib
import os
import secrets
import signal
import socket
import subprocess
import sys
import time

PYTHON = sys.executable


class bcolors:
    KERNEL = '\033[95m'
    PERCEPTILABS = '\033[94m'
    RYGG = '\033[92m'
    ERROR = '\033[31m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    if sys.platform.startswith("win"):
        try:
            import colorama
            colorama.init()
        except:
            KERNEL = ''
            PERCEPTILABS = ''
            RYGG = ''
            WARNING = ''
            FAIL = ''
            ENDC = ''
            BOLD = ''
            UNDERLINE = ''

# fmt: off
MIGRATION_CMD = [PYTHON, "-m", "django", "migrate", "--settings", "rygg.settings"]
SERVICE_CMDS = [
    [PYTHON, "-c", "from perceptilabs.mainServer import main; main()"],
    [PYTHON, "-m", "django", "runserver", "--settings", "rygg.settings", "--noreload"],
    [PYTHON, "-m", "django", "runserver", "--settings", "fileserver.settings", "--noreload"],
    [PYTHON, "-m", "django", "runserver", "localhost:8080", "--settings", "static_file_server.settings", "--noreload"],
    [PYTHON, "-c", "from static_file_server import website_launcher; website_launcher.launchAndKeepAlive()"],
]

# We're assuming everything is running locally
HOST = "127.0.0.1"

PORTS = {
            "kernel": 5000,
            "rygg": 8000,
            "fileserver": 8011,
            "frontend": 8080,
        }
# fmt: on


def check_for_atari():
    if not sys.platform.startswith("win"):
        return

    spec = importlib.util.find_spec("atari_py")
    if spec:
        return

    print(f"{bcolors.WARNING}PerceptiLabs:{bcolors.ENDC} Your environment does not have atari_py installed, so some functionality may not be available")
    print(f"{bcolors.WARNING}PerceptiLabs:{bcolors.ENDC} To install it, please follow the directions at https://github.com/Kojoley/atari-py and then install gym through 'pip install gym[atari]'")

    # give the user a chance to read the message
    time.sleep(1)


def do_migration(pipes):
    migtate_proc = subprocess.run(MIGRATION_CMD, **pipes)
    if migtate_proc.returncode != 0:
        print(f"{bcolors.ERROR}Error:{bcolors.ENDC} Unable to upgrade your perceptilabs database.", file=sys.stderr)
        sys.exit(1)


def start_one(cmd, pipes, api_token):
    env = os.environ.copy()
    env["PL_FILE_SERVING_TOKEN"] = api_token

    return subprocess.Popen(cmd, **pipes, env=env)


def stop_one(proc, wait_secs=5):
    print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} Stopping process {proc.pid}")
    try:
        proc.kill()
        proc.wait(wait_secs)
    except:
        print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} No response. Terminating process {proc.pid}")
        proc.terminate()


def stop(procs):
    for proc in procs:
        stop_one(proc)


def is_alive(proc):
    proc.communicate()
    return proc.returncode == None


def are_all_alive(procs):
    return all([is_alive(p) for p in procs])


def watch(procs, interval_secs=1):
    while True:
        time.sleep(interval_secs)
        if not are_all_alive(procs):
            break

    stop(procs)


def get_pipes(verbosity):
    return {
        "stdout": subprocess.DEVNULL if verbosity < 2 else None,
        "stderr": subprocess.DEVNULL if verbosity < 1 else None,
        "stdin": subprocess.DEVNULL,
    }


class PortPoller:
    def is_port_live(port):
        with socket.socket() as s:
            rc = s.connect_ex((HOST, port))
            return rc == 0

    def get_unresponsive_ports():
        return [
            (name, port)
            for name, port in PORTS.items()
            if not PortPoller.is_port_live(port)
        ]

    def wait_for_ports(interval_secs=3):
        count = 0
        while True:
            unresponsive = PortPoller.get_unresponsive_ports()
            if not any(unresponsive):
                return

            count += 1
            if count > 1:
                print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} Waiting for services to listen on these ports:")
                for s, p in unresponsive:
                    print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC}    {s} on port {p}")
            time.sleep(interval_secs)


def start(verbosity):
    # give the handler closure the shared procs variable
    procs = []

    def handler(signum, frame):
        print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} Received SIGINT (Stop signal)")
        stop(procs)
        sys.exit(0)

    try:
        check_for_atari()
        pipes = get_pipes(verbosity)
        do_migration(pipes)
        api_token = secrets.token_urlsafe(nbytes=64)
        procs = list([start_one(cmd, pipes, api_token) for cmd in SERVICE_CMDS])
        print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} Starting")
        PortPoller.wait_for_ports()
        print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} PerceptiLabs Started")
        print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} PerceptiLabs is running at http://localhost:8080/?token={token}")
        print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} Use Control-C to stop this server and shut down all PerceptiLabs processes.")
        signal.signal(signal.SIGINT, handler)
        watch(procs)
    except Exception as e:
        print(e)
        stop(procs)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", help="set output verbosity (0,1, or 2)", type=int, default=0)
    return parser.parse_args()


def main():
    args = get_args()
    start(args.verbosity)


if __name__ == "__main__":
    main()
