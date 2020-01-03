import os
import sys
import shutil
import logging
import traceback
import sentry_sdk

import utils
from analytics.scraper import get_scraper
from databundle import DataBundle, AzureUploader, AZURE_ACCOUNT_NAME_EU, AZURE_ACCOUNT_KEY_EU, AZURE_CONTAINER_EU, AZURE_ACCOUNT_NAME_US, AZURE_ACCOUNT_KEY_US, AZURE_CONTAINER_US

log = logging.getLogger(__name__)
scraper = get_scraper()

class Server():
    def __init__(self, user=None):
        self.data_bundle = self.setup_scraper()
        self.setup_sentry(user)

    def setup_sentry(self, user=None):
        def strip_unimportant_errors(event, hint):
            log_ignores=['Error in getTestingStatistics', 'Error in getTrainingStatistics', ]

            if 'log_record' in hint:
                if hint['log_record'].msg in log_ignores:
                    return None

            if 'exc_info' in hint:
                from core_new.history import HistoryInputException
                exc_type, exc_value, tb = hint['exc_info']
                if isinstance(exc_value, HistoryInputException):
                    return None
                    
            return event

        sentry_sdk.init("https://9b884d2181284443b90c21db68add4d7@sentry.io/1512385", before_send=strip_unimportant_errors)
        if user:
            with sentry_sdk.configure_scope() as scope:
                scope.user = {"email" : user}

    def setup_scraper(self):
        data_uploaders = [
            AzureUploader(AZURE_ACCOUNT_NAME_EU, AZURE_ACCOUNT_KEY_EU, AZURE_CONTAINER_EU),
            AzureUploader(AZURE_ACCOUNT_NAME_US, AZURE_ACCOUNT_KEY_US, AZURE_CONTAINER_US)        
        ]                               
        data_bundle = DataBundle(data_uploaders)
        utils.dump_system_info(os.path.join(data_bundle.path, 'system_info.json'))
        utils.dump_build_info(os.path.join(data_bundle.path, 'build_info.json'))    

        scraper.start()
        scraper.set_output_directory(data_bundle.path)

        return data_bundle

    def serve_desktop(self, interface, instantly_kill=False): 
        import selectors
        import socket
        import libserver

        sel = selectors.DefaultSelector()

        def accept_wrapper(sock):
            conn, addr = sock.accept()  # Should be ready to read
            log.info("accepted connection from {}".format(addr))
            conn.setblocking(False)
            message = libserver.Message(sel, conn, addr, interface)
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
            scraper.stop()
            
            if not instantly_kill:
                log.info("Copying logfile to data bundle.")
                try:
                    shutil.copyfile('backend.log', os.path.join(data_bundle.path, 'backend.log'))
                except:
                    pass
                
                log.info("Uploading data bundle...")
                self.data_bundle.upload_and_clear()

    def serve_web(self, interface, instantly_kill=False): 
        import websockets

        path='0.0.0.0'
        port=5000
        interface=Message(interface)
        start_server = websockets.serve(interface.interface, path, port)
        log.info("Trying to listen to: " + str(path) + " " + str(port))
        connected=False
        while not connected:
            try:
                asyncio.get_event_loop().run_until_complete(start_server)
                asyncio.get_event_loop().run_forever()
                log.info("Connected")
                connected=True
            except KeyboardInterrupt:
                break
            # except SystemExit:
                # Might not want SystemExit since that will happen whenever someone closes the web browser
            #     break
            except:
                connected=False

    def serve_azure(self, interface, instantly_kill=False):
        pass

    
