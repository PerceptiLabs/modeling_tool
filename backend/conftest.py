import os
import sys
import shutil
import psutil
import pytest
import logging
import tempfile
import pkg_resources
import tensorflow as tf
import numpy as np


log = logging.getLogger(__name__)

@pytest.fixture(scope='session')
def tutorial_data_path():
    path = pkg_resources.resource_filename('perceptilabs', 'tutorial_data')
    yield path

    
@pytest.fixture(autouse=True)
def init_graph():
    #reference: https://stackoverflow.com/questions/56719066/reset-default-graph-upon-exiting-tf-session-in-unit-tests
    with tf.Graph().as_default():
        yield

        
#@pytest.fixture(autouse=True)
#def reset():
#    yield
#    tf.reset_default_graph()        

    
@pytest.fixture()
def temp_path():
    path = tempfile.mkdtemp().replace('\\', '/')

    def make_16x4():
        m1 = np.array([
            [0.1, 0.2, 0.3, 1.0],
            [0.1, 0.2, 0.3, 1.1],        
            [0.1, -1.0, -1.0, 1.0],
            [0.0, 0.1, 1.0, -1.0],
            [0.1, 0.2, 0.3, 1.0],
            [0.1, 0.2, 0.3, 1.1],        
            [0.1, -1.0, -1.0, 1.0],
            [0.0, 0.1, 1.0, -1.0],
            [0.1, 0.2, 0.3, 1.0],
            [0.1, 0.2, 0.3, 1.1],        
            [0.1, -1.0, -1.0, 1.0],
            [0.0, 0.1, 1.0, -1.0],
            [0.1, 0.2, 0.3, 1.0],
            [0.1, 0.2, 0.3, 1.1],        
            [0.1, -1.0, -1.0, 1.0],
            [0.0, 0.1, 1.0, -1.0],
        ])
        np.save(os.path.join(path, '16x4_inputs.npy'), m1)

        m2 = np.array([
            [1, 0, 0],
            [1, 0, 0],        
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 0],
            [1, 0, 0],        
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 0],
            [1, 0, 0],        
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 0],
            [1, 0, 0],        
            [0, 1, 0],
            [0, 0, 1]
        ])
        np.save(os.path.join(path, '16x4_targets.npy'), m2)

        
    # ---- Make datasets ----
    make_16x4()
    
    yield path
    shutil.rmtree(path)

@pytest.fixture()
def temp_path_100x1():
    path = tempfile.mkdtemp().replace('\\', '/')
    def make_linreg():
        m1 = np.arange(100)
        np.save(os.path.join(path, '100x1_inputs.npy'), m1)

        m2 = 0.4 * m1
        np.save(os.path.join(path, '100x1_outputs.npy'), m2)

    make_linreg()
    yield path
    shutil.rmtree(path)

@pytest.fixture(scope='session', autouse=True)
def disable_gpu():
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    yield


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


@pytest.fixture(scope='session', autouse=True)
def temp_path_checkpoints():
    path = tempfile.mkdtemp().replace('\\', '/')
    path = os.path.join(path, 'dummy_model')
    yield path

