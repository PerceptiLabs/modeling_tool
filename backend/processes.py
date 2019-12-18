import os
import time
import psutil
#import _thread
import signal
import logging
import threading


log = logging.getLogger(__name__)


class ProcessDependencyWatcher(threading.Thread):
    # https://stackoverflow.com/questions/1489669/how-to-exit-the-entire-application-from-a-python-thread    
    def __init__(self, pid, sleep_period=1, grace_period=15, verbose=False):
        super().__init__(daemon=True)
        self._pid = pid
        self._sleep_period = sleep_period
        self._grace_period = grace_period
        
    def run(self):
        if self._pid is None:
            log.warning("Monitored process id is None. No monitoring will take place.")
            return

        while True:
            if not psutil.pid_exists(self._pid):
                log.warning("Monitored process {} not found. This process will self terminate in {} seconds".format(self._pid, self._grace_period))                
                time.sleep(self._grace_period) # Give a grace period of N seconds before the process self terminates.
                
                log.warning("Monitored process {} not found. Terminating this process.".format(self._pid))
                os.kill(os.getpid(), 9)

            time.sleep(self._sleep_period)

            
        


    

    
