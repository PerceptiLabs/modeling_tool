#!/usr/bin/env python
import os
import time
import sys

_host = 'localhost'
_port = 8080

def launch():

    command = get_start_command()
    url = get_url()
    os.system(f"{command} {url}")

def get_url():
    url = f"http://{_host}:{_port}"
    token = os.environ.get("PL_FILE_SERVING_TOKEN")
    if not token:
        return url
    return f"{url}/?token={token}"

def get_start_command():
    import platform

    os_platform = platform.system()
    if 'Windows' in os_platform:
        return 'start'
    elif 'Darwin' in os_platform:
        return 'open'
    elif 'Linux' in os_platform:
        return 'xdg-open'
    else:
        raise Exception(f"Unknown platform: {os_platform}")

def awaitHostPortOpen():
    import socket

    # a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # a_socket.settimeout(1)

    location = (_host, _port)

    connection_status = -1

    while connection_status != 0:
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        a_socket.settimeout(0.5)

        connection_status = a_socket.connect_ex(location)
        time.sleep(1)

        a_socket.close()

    # a_socket.close()

def launchAndKeepAlive():
    awaitHostPortOpen()
    launch()
    while True:
        time.sleep(3600)

if __name__ == '__main__':
    launchAndKeepAlive()
