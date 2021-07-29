import logging
import socket
import os
import sys
import shutil
import logging

from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.settings as settings

logger = logging.getLogger(APPLICATION_LOGGER)


class Server():
    def serve_desktop(self, interface, instantly_kill=False): 
        import selectors
        import socket
        from perceptilabs.server.desktop_serverlib import Message

        sel = selectors.DefaultSelector()

        def accept_wrapper(sock):
            conn, addr = sock.accept()  # Should be ready to read
            logger.debug("accepted connection from {}".format(addr))
            conn.setblocking(False)
            message = Message(sel, conn, addr, interface)
            sel.register(conn, selectors.EVENT_READ, data=message)


        host, port = '127.0.0.1', 5000
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            lsock.bind((host, port))
        except OSError as e:
            logger.exception(e)
            return 0
        lsock.listen()
        logger.info("listening on {}:{}".format(host, port))
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)
            
        try:
            if instantly_kill:
                sys.exit(0)
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
                            logger.exception("Main error")
                            message.close()
        except KeyboardInterrupt:
            logger.info("caught keyboard interrupt, exiting")
        except SystemExit:
            logger.info("closing application")
        finally:
            logger.info("Closing selector")        
            sel.close()
            logger.info("All closed")

    def find_free_port(self, hostname, min_port, max_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = min_port
        while port <= max_port:
            try:
                sock.bind((hostname, port))
                sock.close()
                return port
            except OSError:
                port += 1
            raise IOError('no free ports')

    def serve_web(self, interface, instantly_kill=False, port=5000, on_server_started=None): 
        import websockets
        import asyncio
        from perceptilabs.server.web_serverlib import Message

        path='0.0.0.0'
        port = port or self.find_free_port(
            path, settings.TRAINING_PORT_MIN, settings.TRAINING_PORT_MAX)
            
        message = Message(interface)

        if on_server_started:
            on_server_started(path, port)

        async def stop():
            while message.interface.has_remaining_work:
                await asyncio.sleep(1)
        
            duration = 2 if message.interface.has_failed else 15
            logger.info(f"MainInterface indicated no work remaining. Shutting down Kernel in {duration} seconds")
            await asyncio.sleep(duration)                

        async def start_server(stop):
            async with websockets.serve(message.on_message, path, port):
                await stop()

        logger.info("Trying to listen to: " + str(path) + " " + str(port))
        connected=False

        while not connected:
            try:
                if instantly_kill:
                    break
                
                loop = asyncio.new_event_loop()
                loop.run_until_complete(start_server(stop))
                logger.info("Connected")
                connected=True
            except KeyboardInterrupt:
                break
            except:
                connected=False

    def serve_azure(self, interface, instantly_kill=False):
        pass

    
