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
    FILE_NAME = 'app.log'
    
    logging.basicConfig(format=FORMAT,
                        level=logging.INFO,
                        handlers=[
                            logging.StreamHandler(),
                            logging.FileHandler(FILE_NAME)
                        ])
    
if __name__ == "__main__":
    setup_logger()
    appServer.mainServer()
