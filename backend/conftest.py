import os
import sys
import psutil
import pytest
import logging


log = logging.getLogger(__name__)


@pytest.fixture(scope='function', autouse=True)
def print_name_and_memory():
    test_name = os.environ.get('PYTEST_CURRENT_TEST')

    #if os.name == 'nt':
    #    log.info('Initializing test: {}'.format(test_name))
    #else:
    #    import resource
    #    rss_max = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024/1024
    #    log.info('Initializing test: {}. Max RSS: {} [MiB]'.format(test_name, rss_max))


    '''
    def mem_str():
        if sys.platform == 'darwin':
            import resource
            mem_str = 'Virtual memory: {}%, RSS max: {:.2f} [MiB]'.format(psutil.virtual_memory().percent, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024/1024)        
        elif sys.platform == 'linux' or sys.platform == 'linux2':
            import resource            
            mem_str = 'Virtual memory: {}%, RSS max: {:.2f} [MiB]'.format(psutil.virtual_memory().percent, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)    
        else:
            mem_str = 'Virtual memory: {}%'.format(psutil.virtual_memory().percent)
        return mem_str
    '''

    #http://www.pybloggers.com/2016/02/psutil-4-0-0-and-how-to-get-real-process-memory-and-environ-in-python/
    log.info('Initializing test: {}, memory: {}'.format(test_name, psutil.Process().memory_full_info()))
        
    yield

    log.info('Finalizing test: {}, memory: {}'.format(test_name, psutil.Process().memory_full_info()))    


