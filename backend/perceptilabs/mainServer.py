import logging
import sys
import json
import uuid
import logging
import argparse
import threading
import pkg_resources

import perceptilabs.logconf
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


def on_kernel_started(commit_id, data_logger):
    import pkg_resources
    import platform
    import psutil
    import time
    
    data_logger.info(
        'kernel_started',
        extra={
            'namespace': dict(
                cpu_count=psutil.cpu_count(),
                platform={
                    'platform': platform.platform(),
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'processor': platform.processor()
                },
                memory={
                    'phys_total': psutil.virtual_memory().total, # Deceptive naming, but OK according to docs: https://psutil.readthedocs.io/en/latest/
                    'phys_available': psutil.virtual_memory().available,
                    'swap_total': psutil.swap_memory().total,             
                    'swap_free': psutil.swap_memory().free
                },
                python={
                    'version': platform.python_version(),
                    'packages': [p.project_name + ' ' + p.version for p in pkg_resources.working_set]
                }
            )
        }
    )

def main():
    args = get_input_args()
    session_id = uuid.uuid4().hex

    with open(pkg_resources.resource_filename('perceptilabs', 'app_variables.json'), 'r') as f:
        app_variables = json.load(f)

    commit_id = app_variables["BuildVariables"]["CommitId"]
    
    perceptilabs.logconf.setup_application_logger(log_level=args.log_level)
    perceptilabs.logconf.setup_data_logger(is_dev=(commit_id == "Dev"))
    perceptilabs.logconf.set_session_id(session_id)
    
    logger = logging.getLogger(perceptilabs.logconf.APPLICATION_LOGGER)
    data_logger = logging.getLogger(perceptilabs.logconf.DATA_LOGGER)

    from perceptilabs.mainInterface import Interface
    from perceptilabs.server.appServer import Server
    from perceptilabs.utils import frontend_watcher
    from perceptilabs.main_setup import setup_sentry

    if args.frontend_pid is not None:
        logger.info(f"Frontend process id = {args.frontend_pid} specified. Backend will self terminate if frontend is shutdown unexpectedly.")        
        threading.Thread(target=frontend_watcher, args=(args.frontend_pid,), kwargs={'logger': logger}, daemon=True).start()
    else:
        logger.warning("No frontend process id specified. Backend will not self terminate if frontend is shutdown unexpectedly.")
    

    setup_sentry(args.user, commit_id)
    logger.info("Reporting errors with commit id: " + str(commit_id))

    try:
        on_kernel_started(commit_id, data_logger)
    except:
        logger.exception("logging 'on_kernel_started' event failed!")

    logger.info("Reporting errors with commit id: " + str(commit_id))

    message_bus = get_message_bus()
    message_bus.start()
    
    cores=dict()
    dataDict=dict()
    checkpointDict=dict()
    lwDict=dict()
    
    core_interface = Interface(cores, dataDict, checkpointDict, lwDict, args.core_mode)

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
        perceptilabs.logconf.upload_logs(session_id)

if __name__ == "__main__":
    main()
