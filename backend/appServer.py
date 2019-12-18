import os
import sys
import socket
import shutil
import logging
import selectors
import traceback
import sentry_sdk


import utils
import libserver
from analytics.scraper import get_scraper
from databundle import DataBundle, AzureUploader, AZURE_ACCOUNT_NAME_EU, AZURE_ACCOUNT_KEY_EU, AZURE_CONTAINER_EU, AZURE_ACCOUNT_NAME_US, AZURE_ACCOUNT_KEY_US, AZURE_CONTAINER_US

log = logging.getLogger(__name__)
scraper = get_scraper()

def mainServer(instantly_kill=False):
    data_uploaders = [
        AzureUploader(AZURE_ACCOUNT_NAME_EU, AZURE_ACCOUNT_KEY_EU, AZURE_CONTAINER_EU),
        AzureUploader(AZURE_ACCOUNT_NAME_US, AZURE_ACCOUNT_KEY_US, AZURE_CONTAINER_US)        
    ]                               
    data_bundle = DataBundle(data_uploaders)
    utils.dump_system_info(os.path.join(data_bundle.path, 'system_info.json'))
    utils.dump_build_info(os.path.join(data_bundle.path, 'build_info.json'))    

    scraper.start()
    scraper.set_output_directory(data_bundle.path)
    
    sentry_sdk.init("https://9b884d2181284443b90c21db68add4d7@sentry.io/1512385")

    sel = selectors.DefaultSelector()
    cores=dict()
    dataDict=dict()
    checkpointDict=dict()
    lwNetworks=dict()

    def accept_wrapper(sock):
        conn, addr = sock.accept()  # Should be ready to read
        log.info("accepted connection from {}".format(addr))
        conn.setblocking(False)
        message = libserver.Message(sel, conn, addr, cores, dataDict,checkpointDict,lwNetworks)
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
                        sentry_sdk.capture_exception()
                        log.error("main: error: exception for " + str(message.addr) + "\n" + str(traceback.format_exc()))
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
            data_bundle.upload_and_clear()
