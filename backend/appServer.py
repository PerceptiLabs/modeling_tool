import sys
import socket
import selectors
import traceback

import libserver

import sentry_sdk

def mainServer():
    sentry_sdk.init("https://9b884d2181284443b90c21db68add4d7@sentry.io/1512385")

    sel = selectors.DefaultSelector()
    cores=dict()
    dataDict=dict()
    checkpointDict=dict()
    lwNetworks=dict()

    def accept_wrapper(sock):
        conn, addr = sock.accept()  # Should be ready to read
        print("accepted connection from", addr)
        conn.setblocking(False)
        message = libserver.Message(sel, conn, addr, cores, dataDict,checkpointDict,lwNetworks)
        sel.register(conn, selectors.EVENT_READ, data=message)


    host, port = '127.0.0.1', 5000
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # try:
    lsock.bind((host, port))
    # except:
    #     return 0
    lsock.listen()
    print("listening on", (host, port))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception:
                        sentry_sdk.capture_exception()
                        print(
                            "main: error: exception for",
                            f"{message.addr}:\n{traceback.format_exc()}",
                        )
                        message.close()
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    except SystemExit:
        print("closing application")
    finally:
        sel.close()
        print("All closed")