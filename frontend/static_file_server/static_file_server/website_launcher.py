#!/usr/bin/env python
import os
import platform
import time
import socket
import sys

_host = 'localhost'
_port = 8080

def launch():
    os_platform = platform.platform()

    command = None

    if 'Windows' in os_platform:
        command = f'start http://{_host}:{_port}'
    elif 'Darwin' in os_platform:
        command = f'open http://{_host}:{_port}'
    elif 'Linux' in os_platform:
        command = f'xdg-open http://{_host}:{_port}'

    if command:
        os.system(command)

def awaitHostPortOpen():
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