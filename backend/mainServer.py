import logging
import sys

import appServer

def setup_logger():
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
                        level=logging.INFO)
    
if __name__ == "__main__":
    setup_logger()
    import tensorflow as tf
    print("TF GPU Test: ")
    tf.test.is_gpu_available()
    appServer.mainServer()
