import os
import pytest
import logging
import resource

log = logging.getLogger(__name__)


@pytest.fixture(scope='function', autouse=True)
def print_name_and_memory():
    resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    test_name = os.environ.get('PYTEST_CURRENT_TEST')

    rss_max = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024/1024
    
    log.info('Initializing test: {}. Max RSS: {} [MiB]'.format(test_name, rss_max))
    yield
    log.info('Finalizing test: {}'.format(test_name))    


