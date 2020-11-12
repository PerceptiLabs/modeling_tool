import socket
import time
import os
import sys


def check(dest):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect(dest)
            print("connected")
            return True
        except Exception as e:
            return False


def get_dest():

    if os.getenv("DB") != "postgres":
        sys.exit(0)

    host = str(os.getenv("DB_HOST", ""))
    port = int(os.getenv("DB_PORT", 5432))
    if len(host) == 0:
        print("DB_HOST isn't set")
        sys.exit(1)

    return (host, port)


def poll():
    dest = get_dest()
    print(f"Waiting for port {dest}")
    while not check(dest):
        time.sleep(2)


poll()
