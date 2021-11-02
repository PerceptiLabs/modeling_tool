import os
import logging
import argparse
from waitress import serve
from concurrent.futures import ThreadPoolExecutor

import perceptilabs.logconf
import perceptilabs.utils as utils

from perceptilabs.caching.utils import get_preview_cache, get_data_metadata_cache


PORT_RENDERING_KERNEL = 5001
APP_VARIABLES = utils.get_app_variables()        
COMMIT_ID = APP_VARIABLES["BuildVariables"]["CommitId"]

utils.allow_memory_growth_on_gpus()        

    
def get_input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--log-level', default=os.getenv("PL_KERNEL_LOG_LEVEL"), type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Log level name.')
    parser.add_argument('-d', '--debug', default=False, action='store_true', help="Run in debug mode")
    
    args = parser.parse_args()
    return args


def main():
    from perceptilabs.endpoints.base import create_app    
    
    args = get_input_args()

    perceptilabs.logconf.setup_application_logger(log_level=args.log_level)

    logger = logging.getLogger(perceptilabs.logconf.APPLICATION_LOGGER)

    # utils.disable_gpus()  # Rendering and training kernels will compete for resources when running on the same machine. 
    if args.debug:
        app = create_app(
            data_executor=utils.DummyExecutor(),
            preview_cache=get_preview_cache(),                                
            data_metadata_cache=get_data_metadata_cache()
        )            
        app.run(port=PORT_RENDERING_KERNEL, debug=True)
    else:
        app = create_app(
            data_executor=ThreadPoolExecutor(),                
            preview_cache=get_preview_cache(),                
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
