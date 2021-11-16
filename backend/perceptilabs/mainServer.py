import os
import sys
import logging
import argparse

from waitress import serve


import perceptilabs.utils as utils
import perceptilabs.settings as settings
from perceptilabs.caching.utils import get_preview_cache


logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


PORT_RENDERING_KERNEL = 5001
APP_VARIABLES = utils.get_app_variables()        
COMMIT_ID = APP_VARIABLES["BuildVariables"]["CommitId"]


def main():
    utils.setup_sentry()

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', default=False, action='store_true', help="Run in debug mode")
    args = parser.parse_args()
    
    utils.allow_memory_growth_on_gpus()
    
    from perceptilabs.api.base import create_app        

    # utils.disable_gpus()  # Rendering and training kernels will compete for resources when running on the same machine. 
    if args.debug:
        app = create_app(
            preview_cache=get_preview_cache(),                                
        )            
        app.run(port=PORT_RENDERING_KERNEL, debug=True)
    else:
        app = create_app(
            preview_cache=get_preview_cache(),                
        )
        serve(
            app,
            host="0.0.0.0",
            port=PORT_RENDERING_KERNEL,
            expose_tracebacks=True
        )            
        

if __name__ == "__main__":
    main()
