import os
import pytest
import logging


log = logging.getLogger(__name__)


@pytest.fixture(scope='function', autouse=True)
def print_name_and_memory():
    test_name = os.environ.get('PYTEST_CURRENT_TEST')

    if os.name == 'nt':
        log.info('Initializing test: {}'.format(test_name))
    else:
        import resource
        rss_max = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024/1024
        log.info('Initializing test: {}. Max RSS: {} [MiB]'.format(test_name, rss_max))
        
    yield
    log.info('Finalizing test: {}'.format(test_name))    


