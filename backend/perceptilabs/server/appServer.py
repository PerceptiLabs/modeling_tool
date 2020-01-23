import os
import sys
import shutil
import logging

log = logging.getLogger(__name__)

class Server():
    def __init__(self, scraper, data_bundle):
        self.scraper = scraper
        self.data_bundle = data_bundle

    def serve_desktop(self, interface, instantly_kill=False): 
        import selectors
        import socket
        from perceptilabs.server.desktop_serverlib import Message

        sel = selectors.DefaultSelector()

        def accept_wrapper(sock):
            conn, addr = sock.accept()  # Should be ready to read
            log.info("accepted connection from {}".format(addr))
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
            log.exception(e)
            return 0
        lsock.listen()
        log.info("listening on {}:{}".format(host, port))
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
                            log.exception("Main error")
                            message.close()
        except KeyboardInterrupt:
            log.info("caught keyboard interrupt, exiting")
        except SystemExit:
            log.info("closing application")
        finally:
            log.info("Closing selector")        
            sel.close()
            log.info("All closed")        

            log.info("Stopping scraper")
            self.scraper.stop()
            
            if not instantly_kill:
                log.info("Copying logfile to data bundle.")
                try:
                    shutil.copyfile('backend.log', os.path.join(self.data_bundle.path, 'backend.log'))
                except:
                    pass
                
                log.info("Uploading data bundle...")
                self.data_bundle.upload_and_clear()

    def serve_web(self, interface, instantly_kill=False): 
        import websockets
        import asyncio
        from perceptilabs.server.web_serverlib import Message

        path='0.0.0.0'
        port=5000
        interface=Message(interface)
        start_server = websockets.serve(interface.interface, path, port)
        log.info("Trying to listen to: " + str(path) + " " + str(port))
        connected=False
        while not connected:
            try:
                if instantly_kill:
                    break
                asyncio.get_event_loop().run_until_complete(start_server)
                asyncio.get_event_loop().run_forever()
                log.info("Connected")
                connected=True
            except KeyboardInterrupt:
                break
            except:
                connected=False

        log.info("Stopping scraper")
        self.scraper.stop()
        
        if not instantly_kill:
            log.info("Copying logfile to data bundle.")
            try:
                shutil.copyfile('backend.log', os.path.join(self.data_bundle.path, 'backend.log'))
            except:
                pass
            
            log.info("Uploading data bundle...")
            self.data_bundle.upload_and_clear()

    def serve_azure(self, interface, instantly_kill=False):
        pass

    
