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
from perceptilabs.issues import IssueHandler
from perceptilabs.caching.utils import get_preview_cache, get_data_metadata_cache


PORT_RENDERING_KERNEL = 5001
APP_VARIABLES = utils.get_app_variables()        
COMMIT_ID = APP_VARIABLES["BuildVariables"]["CommitId"]

utils.allow_memory_growth_on_gpus()        

    
def get_input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--log-level', default=os.getenv("PL_KERNEL_LOG_LEVEL"), type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Log level name.')
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
    parser.add_argument('-m','--mode', default=os.getenv("PL_KERNEL_MODE", 'training'), type=str, choices=['training', 'testing', 'rendering'])
    parser.add_argument('-d', '--debug', default=False, action='store_true', help="Run in debug mode")
    
    args = parser.parse_args()
    return args


def main():
    args = get_input_args()
    session_id = uuid.uuid4().hex
    issue_handler = IssueHandler()

    perceptilabs.logconf.setup_application_logger(log_level=args.log_level)
    perceptilabs.logconf.setup_console_logger(queue = issue_handler._logs)

    logger = logging.getLogger(perceptilabs.logconf.APPLICATION_LOGGER)
    
    # utils.disable_gpus()  # Rendering and training kernels will compete for resources when running on the same machine. 
    from perceptilabs.endpoints.base import create_app
    import perceptilabs.session.utils as session_utils

    if args.debug:
        app = create_app(
            data_executor=utils.DummyExecutor(),
            preview_cache=get_preview_cache(),                                
            session_executor=session_utils.get_session_executor(),
            data_metadata_cache=get_data_metadata_cache()
        )            
        app.run(port=PORT_RENDERING_KERNEL, debug=True)
    else:
        from waitress import serve
        from concurrent.futures import ThreadPoolExecutor
        
        app = create_app(
            data_executor=ThreadPoolExecutor(),                
            preview_cache=get_preview_cache(),                
            session_executor=session_utils.get_session_executor(),
            data_metadata_cache=get_data_metadata_cache()
        )
        serve(
            app,
            host="0.0.0.0",
            port=PORT_RENDERING_KERNEL,
            expose_tracebacks=True
        )            
        

if __name__ == "__main__":
    main()
