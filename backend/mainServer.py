import logging
import sys
import argparse
import json

from processes import ProcessDependencyWatcher
from mainInterface import Interface
from server.appServer import Server

from main_setup import setup_scraper, setup_sentry, scraper


def get_input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--frontend-pid', default=None, type=int,
                        help='Frontend process id.')
    parser.add_argument('-l','--log-level', default='WARNING', type=str,
                        help='Log level name.')
    parser.add_argument('-k','--instantly-kill', default=False, type=bool,
                        help="Set this to instantly kill the core, for test purposes.")
    parser.add_argument('-u', '--user', default="dev@dev.com", type=str,
                        help="Set this to attach a user to all Sentry logs.")
    parser.add_argument('-p','--platform', default='desktop', type=str, 
                        help="Sets what type of frontend you want to communicate with. Can be either 'desktop' or 'browser'.")
    parser.add_argument('-e', '--error', default=False, type=bool, 
                        help="Force an error to see that all the error logging works as it should")
    args = parser.parse_args()
    return args


def setup_logger(log_level):
    """ Sets up logging for the application.

    In other modules, simply call log = logging.getLogger(__name__) after importing logging. 
    In production, set the logging level to something higher (e.g., ERROR). 

    Levels:
        DEBUG: Detailed information, for diagnosing problems. 
        INFO: Confirm things are working as expected. 
        WARNING: Something unexpected happened, or indicative of some problem. But the software is still working as expected. 
        ERROR: More serious problem, the software is not able to perform some function. 
        CRITICAL: A serious error, the program itself may be unable to continue running. 
    """
    FORMAT = '%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s'
    FILE_NAME = 'backend.log'
    
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s',
                        level=logging.getLevelName(log_level))
    
if __name__ == "__main__":
    args = get_input_args()

    setup_logger(args.log_level)
    ProcessDependencyWatcher(args.frontend_pid).start()

    log = logging.getLogger(__name__)

    with open('app_variables.json', 'r') as f:
        app_variables = json.load(f)

    commit_id = app_variables["BuildVariables"]["CommitId"]
    log.info("Reporting errors with commit id: " + str(commit_id))
    
    cores=dict()
    dataDict=dict()
    checkpointDict=dict()
    lwDict=dict()

    core_interface = Interface(cores, dataDict, checkpointDict, lwDict)

    data_bundle = setup_scraper()
    setup_sentry(args.user, commit_id)

    if args.error:
        raise Exception("Test error")

    server = Server(scraper, data_bundle)
    if args.platform == 'desktop':
        server.serve_desktop(core_interface, args.instantly_kill)
    elif args.platform == 'browser':
        server.serve_web(core_interface, args.instantly_kill)
