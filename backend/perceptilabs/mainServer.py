import logging
import sys
import json
import uuid
import logging
import argparse
import threading
import pkg_resources

import perceptilabs.logconf
import perceptilabs.utils as utils
from perceptilabs.messaging.zmq_wrapper import get_message_bus
from perceptilabs.issues import IssueHandler


def get_input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--log-level', default=None, type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Log level name.')
    parser.add_argument('-k','--instantly-kill', default=False, type=bool,
                        help="Set this to instantly kill the core, for test purposes.")
    parser.add_argument('-u', '--user', default="dev@dev.com", type=str,
                        help="Set this to attach a user to all Sentry logs.")
    parser.add_argument('-p','--platform', default='browser', type=str, choices=['desktop', 'browser'],
                        help="Sets what type of frontend you want to communicate with. Can be either 'desktop' or 'browser'.")
    parser.add_argument('-e', '--error', default=False, type=bool, 
                        help="Force an error to see that all the error logging works as it should")
    args = parser.parse_args()
    return args


def main():
    args = get_input_args()
    session_id = uuid.uuid4().hex
    issue_handler = IssueHandler()

    with open(pkg_resources.resource_filename('perceptilabs', 'app_variables.json'), 'r') as f:
        app_variables = json.load(f)

    commit_id = app_variables["BuildVariables"]["CommitId"]
    
    perceptilabs.logconf.setup_application_logger(log_level=args.log_level)
    perceptilabs.logconf.setup_data_logger(is_dev=(commit_id == "Dev"))
    perceptilabs.logconf.set_session_id(session_id)
    perceptilabs.logconf.setup_console_logger(queue = issue_handler._logs)

    logger = logging.getLogger(perceptilabs.logconf.APPLICATION_LOGGER)
    data_logger = logging.getLogger(perceptilabs.logconf.DATA_LOGGER)

    from perceptilabs.mainInterface import Interface
    from perceptilabs.server.appServer import Server
    from perceptilabs.main_setup import setup_sentry

    setup_sentry(args.user, commit_id)
    logger.info("Reporting errors with commit id: " + str(commit_id))

    message_bus = get_message_bus()
    message_bus.start()
    
    cores=dict()
    dataDict=dict()
    checkpointDict=dict()
    lwDict=dict()
    
    core_interface = Interface(cores, dataDict, checkpointDict, lwDict, issue_handler, session_id=session_id)

    if args.error:
        raise Exception("Test error")

    print("PerceptiLabs is ready...")

    try:
        server = Server()
        if args.platform == 'desktop':
            server.serve_desktop(core_interface, args.instantly_kill)
        elif args.platform == 'browser':
            server.serve_web(core_interface, args.instantly_kill)
        message_bus.stop()            
    except Exception as e:
        logger.exception("Exception in server")
    finally:
        zip_name = utils.format_logs_zipfile_name(session_id)
        perceptilabs.logconf.upload_logs(zip_name)

if __name__ == "__main__":
    main()
