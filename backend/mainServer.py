import logging
import sys
import argparse

from processes import ProcessDependencyWatcher
import appServer


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
    
    appServer.mainServer(args.instantly_kill, args.user)
