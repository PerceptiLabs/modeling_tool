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
import pandas as pd


from perceptilabs.core_new.layers.templates import J2Engine
from perceptilabs.core_new.layers.templates.utils import render_and_execute_macro
from perceptilabs.script import TEMPLATE_DIRECTORIES
from perceptilabs.layers.helper import load_code_as_module

log = logging.getLogger(__name__)

@pytest.fixture(scope='session')
def script_factory():
    yield ScriptFactory()

    
@pytest.fixture(scope='session')
def script_factory_tf2x():
    yield ScriptFactory(mode='tf2x')


@pytest.fixture(scope='session')
def tutorial_data_path():
    path = pkg_resources.resource_filename('perceptilabs', 'tutorial_data')
    yield path


@pytest.fixture(autouse=True, scope='function')
def set_seeds():
    import random
    random.seed(42)
    
    import numpy as np
    np.random.seed(42)
    
    from tensorflow.python.framework import random_seed
    random_seed.set_seed(42)

    
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

    
@pytest.fixture(scope='function')
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
def csv_path(temp_path):
    df = pd.DataFrame({
        'x1': [1.0, 2.0, 3.0],
        'y1': [10.0, 40.0, 50.0]
    })
    path = os.path.join(temp_path, 'data.csv')
    df.to_csv(path, index=False)
    yield path
    

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


@pytest.fixture(scope='session')    
def make_graph_spec():
    from perceptilabs.layers.specbase import LayerConnection
    from perceptilabs.layers.datadata.spec import DataDataSpec, DataSource
    from perceptilabs.layers.processonehot.spec import ProcessOneHotSpec
    from perceptilabs.layers.processreshape.spec import ProcessReshapeSpec
    from perceptilabs.layers.deeplearningfc.spec import DeepLearningFcSpec
    from perceptilabs.layers.trainclassification.spec import TrainClassificationSpec
    from perceptilabs.graph.spec import GraphSpec    
    import tempfile


    
    def fn_make_graph_spec(temp_path_checkpoints, inputs_path, targets_path, learning_rate=0.3, checkpoint_path=None, distributed=False, n_epochs=200, early_stopping=False, load_checkpoint=True): # TODO: fix checkpoint path. it can't be none
        checkpoint_path = checkpoint_path or temp_path_checkpoints
        
        # --- CONNECTIONS ---
        conn_inputs_to_fc = LayerConnection(src_id='layer_inputs', src_var='output', dst_id='layer_fc', dst_var='input')
        conn_fc_to_train = LayerConnection(src_id='layer_fc', src_var='output', dst_id='layer_train', dst_var='predictions')
    
        conn_labels_to_train = LayerConnection(src_id='layer_labels', src_var='output', dst_id='layer_train', dst_var='labels')
        # --- LAYER SPECS ---
        layer_inputs = DataDataSpec(
            id_='layer_inputs',
            name='layer_inputs',
            sources=[DataSource(
                type_='file',
                path=inputs_path.replace('\\','/'),
                ext='.npy',
                split=(70, 20, 10)            
            )],
            checkpoint_path=checkpoint_path,
            forward_connections=(conn_inputs_to_fc,)
        )
        layer_fc = DeepLearningFcSpec(
            id_='layer_fc',
            name='layer_fc',        
            n_neurons=3,
            checkpoint_path=checkpoint_path,
            backward_connections=(conn_inputs_to_fc,),
            forward_connections=(conn_fc_to_train,)
        )
        layer_labels = DataDataSpec(
            id_='layer_labels',
            name='layer_labels',
            sources=[DataSource(
                type_='file',
                path=targets_path.replace('\\','/'),
                ext='.npy',
                split=(70, 20, 10)            
            )],
            checkpoint_path=checkpoint_path,
            forward_connections=(conn_labels_to_train,)
        )
        layer_train = TrainClassificationSpec(
            id_='layer_train',
            name='layer_train',
            batch_size=8,
            optimizer='SGD',
            learning_rate=learning_rate,
            n_epochs=n_epochs,
            distributed=distributed,
            checkpoint_path=checkpoint_path,
            load_checkpoint=load_checkpoint,
            backward_connections=(conn_labels_to_train, conn_fc_to_train),
            connection_labels=conn_labels_to_train,
            connection_predictions=conn_fc_to_train,
            stop_condition='TargetAccuracy' if early_stopping else 'Epochs',
            target_acc=50 if early_stopping else None
        )
    
        graph_spec = GraphSpec([
            layer_inputs,
            layer_fc,
            layer_labels,
            layer_train
        ])
        return graph_spec
    
    yield fn_make_graph_spec


@pytest.fixture(scope='function')
def classification_spec_basic(make_graph_spec, temp_path, temp_path_checkpoints):
    graph_spec = make_graph_spec(
        temp_path_checkpoints, 
        os.path.join(temp_path, '16x4_inputs.npy'),
        os.path.join(temp_path, '16x4_targets.npy')
    )        
    yield graph_spec


@pytest.fixture(scope='session')
def script_factory():
    from perceptilabs.script import ScriptFactory    
    yield ScriptFactory()

    
@pytest.fixture(scope='session')
def script_factory_tf2x():
    from perceptilabs.script import ScriptFactory        
    yield ScriptFactory(mode='tf2x')
