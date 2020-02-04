import pytest

import time
import psutil
from multiprocessing import Process


from perceptilabs.processes import ProcessDependencyWatcher

def proc1_fn(duration):
    time.sleep(duration)

def proc2_fn(pid):
    fm = ProcessDependencyWatcher(pid=pid, sleep_period=0.1, grace_period=0.1)
    fm.start()

    while True: # Infinite loop. This process must be killed to terminate.
        time.sleep(10) 

def test_frontend_watcher():
    ''' A watching process is given 1s to terminate after a watched process has finished. '''
        
    proc1 = Process(target=proc1_fn, args=(0.5,), daemon=False)
    proc1.start()
    
    proc2 = Process(target=proc2_fn, args=(proc1.pid,), daemon=False)
    proc2.start()

    assert proc1.is_alive()
    assert proc2.is_alive()        

    proc1.join()
    proc2.join(timeout=1) 
    assert not proc2.is_alive()
