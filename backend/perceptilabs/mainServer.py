import asyncio
import logging
import sys
import json
import uuid
import logging
import argparse
import threading
import pkg_resources
import tensorflow as tf
import os


import perceptilabs.logconf
import perceptilabs.utils as utils
from perceptilabs.main_setup import setup_sentry, set_sentry_tag
from perceptilabs.messaging.zmq_wrapper import get_message_bus
from perceptilabs.issues import IssueHandler

APP_VARIABLES = utils.get_app_variables()        
COMMIT_ID = APP_VARIABLES["BuildVariables"]["CommitId"]

setup_sentry(COMMIT_ID)
set_sentry_tag('error-type', 'startup-error')


if utils.is_tf2x():
    tf.enable_v2_behavior()
else:
    tf.disable_v2_behavior()    

    
def get_input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--log-level', default=os.getenv("PL_KERNEL_LOG_LEVEL"), type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Log level name.')
    parser.add_argument('-t','--trainer', default=os.getenv("PL_KERNEL_TRAINER", "core_v2"), type=str, choices=['core_v2', 'standard'], help='Which trainer to use.')
    parser.add_argument('-k','--instantly-kill', default=False, type=bool,
                        help="Set this to instantly kill the core, for test purposes.")
    parser.add_argument('-u', '--user', default="dev@dev.com", type=str,
                        help="Set this to attach a user to all Sentry logs.")
    parser.add_argument('-p','--platform', default='browser', type=str, choices=['desktop', 'browser'],
                        help="Sets what type of frontend you want to communicate with. Can be either 'desktop' or 'browser'.")
    parser.add_argument('-e', '--error', default=False, type=bool, 
                        help="Force an error to see that all the error logging works as it should")
    parser.add_argument('-a','--allow-headless', default=False, action='store_true',
                        help="Allow headless mode.")
    args = parser.parse_args()
    return args


def main():
    args = get_input_args()
    session_id = uuid.uuid4().hex
    issue_handler = IssueHandler()

    if args.trainer == 'standard' and not utils.is_tf2x():
        raise RuntimeError("The standard trainer is currently only supported for tf2x")
    
    perceptilabs.logconf.setup_application_logger(log_level=args.log_level)
    perceptilabs.logconf.setup_data_logger(is_dev=(COMMIT_ID == "Dev"))
    perceptilabs.logconf.set_session_id(session_id)
    perceptilabs.logconf.setup_console_logger(queue = issue_handler._logs)

    logger = logging.getLogger(perceptilabs.logconf.APPLICATION_LOGGER)
    data_logger = logging.getLogger(perceptilabs.logconf.DATA_LOGGER)

    if utils.is_tf2x():
        logger.warning("Running TensorFlow version >= 2.0. Experimental support only!")
    
    from perceptilabs.mainInterface import Interface
    from perceptilabs.server.appServer import Server



    logger.info("Reporting errors with commit id: " + str(COMMIT_ID))

    cores=dict()
    dataDict=dict()
    checkpointDict=dict()
    lwDict=dict()
    
    core_interface = Interface(cores, dataDict, checkpointDict, lwDict, issue_handler, session_id=session_id, allow_headless=args.allow_headless, trainer=args.trainer)

    from perceptilabs.memorywatcher import MemoryWatcher
    memory_watcher = MemoryWatcher(issue_handler=issue_handler, core_interfaces=cores)
    memory_watcher.initialize(asyncio.get_event_loop())

    
    if args.error:
        raise Exception("Test error")

    set_sentry_tag('error-type', 'internal-error')    
    print("PerceptiLabs is ready...")

    try:
        server = Server()
        if args.platform == 'desktop':
            server.serve_desktop(core_interface, args.instantly_kill)
        elif args.platform == 'browser':
            server.serve_web(core_interface, args.instantly_kill)
    except Exception as e:
        logger.exception("Exception in server")
    finally:
        zip_name = utils.format_logs_zipfile_name(session_id)
        perceptilabs.logconf.upload_logs(zip_name)

if __name__ == "__main__":
    main()
