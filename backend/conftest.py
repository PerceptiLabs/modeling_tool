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


from perceptilabs.core_new.layers.templates import J2Engine
from perceptilabs.core_new.layers.templates.utils import render_and_execute_macro
from perceptilabs.script import TEMPLATE_DIRECTORIES
from perceptilabs.layers.helper import load_code_as_module

log = logging.getLogger(__name__)

@pytest.fixture(scope='session')
def tutorial_data_path():
    path = pkg_resources.resource_filename('perceptilabs', 'tutorial_data')
    yield path

    
@pytest.fixture(autouse=True)
def init_graph(request):
    #reference: https://stackoverflow.com/questions/56719066/reset-default-graph-upon-exiting-tf-session-in-unit-tests
    tf.reset_default_graph()
    tf.enable_v2_behavior()
    
    if 'tf2x' in request.keywords:
        tf.enable_eager_execution()
        yield
    else:
        tf.disable_eager_execution()        
        with tf.Graph().as_default():
            yield

    
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


@pytest.fixture(scope='function', autouse=True)
def temp_path_checkpoints():
    path = tempfile.mkdtemp()
    path = os.path.join(path, 'dummy_model', 'checkpoint')
    path = path.replace('\\', '/')
    yield path

    
@pytest.fixture(scope='session')
def load_jinja_macro():    
    j2_engine = J2Engine(TEMPLATE_DIRECTORIES)

    def closure(macro_file, macro_name, macro_parameters=None, preamble=None):
        preamble = preamble + '\n' if preamble else ''

        def format_param(x):
            if isinstance(x, str):
                x = f"'{x}'"
            return x

        # Construct jinja template
        template  = preamble
        template += "{% from '" + macro_file + "' import " + macro_name + " %}\n"

        if macro_parameters:
            template += "{{ " + macro_name + "(\n"
            for param_name, param_value in macro_parameters.items():
                template += f"    {param_name}={format_param(param_value)},\n"
            template += ") | remove_spaces(4) }}\n"
        else:
            template += "{{ " + macro_name + "() | remove_spaces(4) }}\n"
            
        template = template.strip()

        # Execute code
        code = j2_engine.render_string(template)
        module = load_code_as_module(code)
        
        return module
    
    yield closure
