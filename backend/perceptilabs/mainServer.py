import sys
import json
import logging
import argparse
import threading
import pkg_resources


from perceptilabs.messaging.zmq_wrapper import get_message_bus

def get_input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--frontend-pid', default=None, type=int,
                        help='Frontend process id.')
    parser.add_argument('-l','--log-level', default=None, type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Log level name.')
    parser.add_argument('-m','--core-mode', default='v2', type=str, choices=['v1', 'v2'],
                        help='Specifies which version of the core to run.')
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


def setup_logger(log_level, core_mode):
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

    if log_level is None and core_mode == 'v1':
        log_level = 'WARNING'
    elif log_level is None:
        log_level = 'INFO'            
    
    FORMAT = '%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s'
    FILE_NAME = 'backend.log'
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s',
        level=logging.getLevelName(log_level),
        # handlers=[
        #     logging.FileHandler("kernel.log"),
        #     logging.StreamHandler()
        # ]
    )

    
def main():
    args = get_input_args()

    setup_logger(args.log_level, args.core_mode)
    log = logging.getLogger(__name__)

    from perceptilabs.mainInterface import Interface
    from perceptilabs.server.appServer import Server
    from perceptilabs.utils import frontend_watcher
    from perceptilabs.main_setup import setup_scraper, setup_sentry, scraper

    if args.frontend_pid is not None:
        log.info(f"Frontend process id = {args.frontend_pid} specified. Backend will self terminate if frontend is shutdown unexpectedly.")        
        threading.Thread(target=frontend_watcher, args=(args.frontend_pid,), kwargs={'log': log}, daemon=True).start()
    else:
        log.warning("No frontend process id specified. Backend will not self terminate if frontend is shutdown unexpectedly.")
    
    with open(pkg_resources.resource_filename('perceptilabs', 'app_variables.json'), 'r') as f:
        app_variables = json.load(f)

    commit_id = app_variables["BuildVariables"]["CommitId"]

    setup_sentry(args.user, commit_id)
    log.info("Reporting errors with commit id: " + str(commit_id))

    message_bus = get_message_bus()
    message_bus.start()
    
    cores=dict()
    dataDict=dict()
    checkpointDict=dict()
    lwDict=dict()
    
    core_interface = Interface(cores, dataDict, checkpointDict, lwDict, args.core_mode)

    data_bundle = setup_scraper()


    if args.error:
        raise Exception("Test error")

    print("PerceptiLabs is ready...")

    server = Server(scraper, data_bundle)
    if args.platform == 'desktop':
        server.serve_desktop(core_interface, args.instantly_kill)
    elif args.platform == 'browser':
        server.serve_web(core_interface, args.instantly_kill)

    message_bus.stop()

if __name__ == "__main__":
    main()
