import os
import pytest
import pandas as pd
import tempfile
import numpy as np
from unittest.mock import MagicMock


from perceptilabs.lwcore import LightweightCore
from perceptilabs.utils import sanitize_path
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.layers.iooutput.spec import OutputLayerSpec
from perceptilabs.layers.ioinput.spec import InputLayerSpec
from perceptilabs.layers.iooutput.spec import OutputLayerSpec
from perceptilabs.data.base import DataLoader, FeatureSpec
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.layers.datadata.spec import DataSource
from perceptilabs.layers.specbase import LayerConnection


@pytest.fixture()
def x1():
    yield [123.0, 24.0, 13.0, 45.0, -10.0]

    
@pytest.fixture()
def y1():
    yield [1.0, 2.0, 3.0, 4.0, -1.0]    
    
    
@pytest.fixture()
def csv_path(temp_path, x1, y1):
    file_path = os.path.join(temp_path, 'data.csv')
    df = pd.DataFrame({'x1': x1, 'y1': y1})
    df.to_csv(file_path, index=False)    
    yield file_path

    
@pytest.fixture()
def graph_spec(csv_path):
    gsb = GraphSpecBuilder()
    dirpath = tempfile.mkdtemp()
    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'datatype': 'numerical', 'feature_name': 'x1', 'file_path': csv_path, 'checkpoint_path':dirpath}
    )
    id2 = gsb.add_layer(
        'DeepLearningFC',
        settings={'n_neurons': 1}
    )
    id3 = gsb.add_layer(
        'IoOutput',
        settings={'datatype': 'numerical', 'feature_name': 'y1', 'file_path': csv_path}
    )

    # Connect the layers
    gsb.add_connection(
        source_id=id1, source_var='output',
        dest_id=id2, dest_var='input'
    )
    gsb.add_connection(
        source_id=id2, source_var='output',
        dest_id=id3, dest_var='input'
    )

    graph_spec = gsb.build()
    return graph_spec



@pytest.fixture(scope='function')
def graph_spec_pre_datawiz(temp_path_checkpoints):
    n_classes = 10
    n_samples = 30

    #f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    #mat = np.random.random((n_samples, 28*28*1))
    #np.save(f1.name, mat)

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    mat = np.random.random((n_samples, 784))
    df = pd.DataFrame.from_records(mat, columns=['col_'+str(x) for x in range(784)])
    df.to_csv(f1.name, index=False)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)

    input_data = DataSource(type_='file', path=inputs_path, ext='.csv')
    label_data = DataSource(type_='file', path=labels_path, ext='.npy')    
    
    builder = GraphSpecBuilder()

    # Branch 1 (Inputs)
    builder.add_layer('DataData', settings={'id_': '1', 'sources': (input_data,)})
    builder.add_layer('ProcessReshape', settings={'id_': '3', 'shape': (28, 28, 1)})
    builder.add_layer('DeepLearningFC', settings={'id_': '4'})
    builder.add_connection('1', 'output', '3', 'input')
    builder.add_connection('3', 'output', '4', 'input')

    # Branch 2 (Labels)
    builder.add_layer('DataData', settings={'id_': '2', 'sources': (label_data,)})    
    builder.add_layer('ProcessOneHot', settings={'id_': '5'})
    builder.add_connection('2', 'output', '5', 'input')                

    # Merge into Training Layer
    conn1 = LayerConnection(src_id='4', src_var='output', dst_id='6', dst_var='predictions')
    conn2 = LayerConnection(src_id='5', src_var='output', dst_id='6', dst_var='labels')      
    
    builder.add_layer('TrainNormal', settings={
        'id_': '6', 'connection_predictions': conn1, 'connection_labels': conn2
    })
    builder.add_connection_object(conn1)
    builder.add_connection_object(conn2)

    graph_spec = builder.build()
    yield graph_spec
    
    f1.close()
    f2.close()


@pytest.fixture(scope='function')
def graph_spec_partial_pre_datawiz(temp_path_checkpoints):
    n_classes = 10
    n_samples = 30

    #f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    #mat = np.random.random((n_samples, 28*28*1))
    #np.save(f1.name, mat)

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    mat = np.random.random((n_samples, 784))
    df = pd.DataFrame.from_records(mat, columns=['col_'+str(x) for x in range(784)])
    df.to_csv(f1.name, index=False)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)

    input_data = DataSource(type_='file', path=inputs_path, ext='.csv')
    label_data = DataSource(type_='file', path=labels_path, ext='.npy')    
    
    builder = GraphSpecBuilder()

    # Branch 1 (Inputs)
    builder.add_layer('DataData', settings={'id_': '1', 'sources': (input_data,)})
    builder.add_layer('ProcessReshape', settings={'id_': '3', 'shape': (28, 28, 1)})
    builder.add_layer('DeepLearningFC', settings={'id_': '4'})
    builder.add_connection('1', 'output', '3', 'input')
    builder.add_connection('3', 'output', '4', 'input')

    # Branch 2 (Labels)
    builder.add_layer('ProcessOneHot', settings={'id_': '5'})

    # Merge into Training Layer
    conn1 = LayerConnection(src_id='4', src_var='output', dst_id='6', dst_var='predictions')
    conn2 = LayerConnection(src_id='5', src_var='output', dst_id='6', dst_var='labels')      
    
    builder.add_layer('TrainNormal', settings={
        'id_': '6', 'connection_predictions': conn1, 'connection_labels': conn2
    })
    builder.add_connection_object(conn1)
    builder.add_connection_object(conn2)

    graph_spec = builder.build()
    yield graph_spec

    f1.close()
    f2.close()

@pytest.fixture(scope='function')
def graph_spec_syntax_error(temp_path_checkpoints):
    n_classes = 10
    n_samples = 30

    #f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    #mat = np.random.random((n_samples, 28*28*1))
    #np.save(f1.name, mat)

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    mat = np.random.random((n_samples, 784))
    df = pd.DataFrame.from_records(mat, columns=['col_'+str(x) for x in range(784)])
    df.to_csv(f1.name, index=False)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)

    input_data = DataSource(type_='file', path=inputs_path, ext='.csv')
    label_data = DataSource(type_='file', path=labels_path, ext='.npy')    
    
    builder = GraphSpecBuilder()

    # Branch 1 (Inputs)
    builder.add_layer('DataData', settings={'id_': '1', 'sources': (input_data,)})
    builder.add_layer('ProcessReshape', settings={
        'id_': '3',
        'shape': (28, 28, 1),
        'custom_code': "print('hello')\n!!!"  # Causes SyntaxError due to exclamation marks
    })
    builder.add_layer('DeepLearningFC', settings={'id_': '4'})
    builder.add_connection('1', 'output', '3', 'input')
    builder.add_connection('3', 'output', '4', 'input')

    # Branch 2 (Labels)
    builder.add_layer('DataData', settings={'id_': '2', 'sources': (label_data,)})    
    builder.add_layer('ProcessOneHot', settings={'id_': '5'})
    builder.add_connection('2', 'output', '5', 'input')                

    # Merge into Training Layer
    conn1 = LayerConnection(src_id='4', src_var='output', dst_id='6', dst_var='predictions')
    conn2 = LayerConnection(src_id='5', src_var='output', dst_id='6', dst_var='labels')      
    
    builder.add_layer('TrainNormal', settings={
        'id_': '6', 'connection_predictions': conn1, 'connection_labels': conn2
    })
    builder.add_connection_object(conn1)
    builder.add_connection_object(conn2)
    
    graph_spec = builder.build()
    yield graph_spec
    f1.close()
    f2.close()
    
@pytest.fixture(scope='function')
def graph_spec_runtime_error(temp_path_checkpoints):
    n_classes = 10
    n_samples = 30

    #f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    #mat = np.random.random((n_samples, 28*28*1))
    #np.save(f1.name, mat)

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    mat = np.random.random((n_samples, 784))
    df = pd.DataFrame.from_records(mat, columns=['col_'+str(x) for x in range(784)])
    df.to_csv(f1.name, index=False)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)

    input_data = DataSource(type_='file', path=inputs_path, ext='.csv')
    label_data = DataSource(type_='file', path=labels_path, ext='.npy')    
    
    builder = GraphSpecBuilder()

    # Branch 1 (Inputs)
    builder.add_layer('DataData', settings={'id_': '1', 'sources': (input_data,)})
    builder.add_layer('ProcessReshape', settings={'id_': '3', 'shape': (28, 28, 1)})
    builder.add_layer('ProcessReshape', settings={
        'id_': '3',
        'shape': (28, 28, 1),
        'custom_code': "print('hello')\n1/0"  # Causes Runtime error by zero division
    })
    builder.add_layer('DeepLearningFC', settings={'id_': '4'})
    builder.add_connection('1', 'output', '3', 'input')
    builder.add_connection('3', 'output', '4', 'input')

    # Branch 2 (Labels)
    builder.add_layer('DataData', settings={'id_': '2', 'sources': (label_data,)})    
    builder.add_layer('ProcessOneHot', settings={'id_': '5'})
    builder.add_connection('2', 'output', '5', 'input')                

    # Merge into Training Layer
    conn1 = LayerConnection(src_id='4', src_var='output', dst_id='6', dst_var='predictions')
    conn2 = LayerConnection(src_id='5', src_var='output', dst_id='6', dst_var='labels')      
    
    builder.add_layer('TrainNormal', settings={
        'id_': '6', 'connection_predictions': conn1, 'connection_labels': conn2
    })
    builder.add_connection_object(conn1)
    builder.add_connection_object(conn2)

    graph_spec = builder.build()
    yield graph_spec

    f1.close()
    f2.close()
    
@pytest.fixture(scope='function')
def graph_spec_runtime_error_training(temp_path_checkpoints):
    n_classes = 10
    n_samples = 30

    #f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    #mat = np.random.random((n_samples, 28*28*1))
    #np.save(f1.name, mat)

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    mat = np.random.random((n_samples, 784))
    df = pd.DataFrame.from_records(mat, columns=['col_'+str(x) for x in range(784)])
    df.to_csv(f1.name, index=False)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)

    input_data = DataSource(type_='file', path=inputs_path, ext='.csv')
    label_data = DataSource(type_='file', path=labels_path, ext='.npy')    
    
    builder = GraphSpecBuilder()

    # Branch 1 (Inputs)
    builder.add_layer('DataData', settings={'id_': '1', 'sources': (input_data,)})
    builder.add_layer('ProcessReshape', settings={'id_': '3', 'shape': (28, 28, 1)})
    builder.add_layer('ProcessReshape', settings={'id_': '3', 'shape': (28, 28, 1)})
    builder.add_layer('DeepLearningFC', settings={'id_': '4'})
    builder.add_connection('1', 'output', '3', 'input')
    builder.add_connection('3', 'output', '4', 'input')

    # Branch 2 (Labels)
    builder.add_layer('DataData', settings={'id_': '2', 'sources': (label_data,)})    
    builder.add_layer('ProcessOneHot', settings={'id_': '5'})
    builder.add_connection('2', 'output', '5', 'input')                

    # Merge into Training Layer
    conn1 = LayerConnection(src_id='4', src_var='output', dst_id='6', dst_var='predictions')
    conn2 = LayerConnection(src_id='5', src_var='output', dst_id='6', dst_var='labels')      
    
    builder.add_layer('TrainNormal', settings={
        'id_': '6', 'connection_predictions': conn1, 'connection_labels': conn2,
        'custom_code': "print('hello')\n1/0"  # Causes Runtime error by zero division
        
    })
    builder.add_connection_object(conn1)
    builder.add_connection_object(conn2)

    graph_spec = builder.build()
    yield graph_spec
    
    f1.close()
    f2.close()
    

@pytest.fixture(scope='function')
def graph_spec_pre_datawiz_with_strings(temp_path_checkpoints):
    n_classes = 10
    n_samples = 30

    #f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    #mat = np.random.random((n_samples, 28*28*1))
    #np.save(f1.name, mat)

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    mat = np.random.random((n_samples, 784))
    df = pd.DataFrame.from_records(mat, columns=['col_'+str(x) for x in range(784)])
    
    df['col_0'] = df['col_0'].astype(str)
    df['col_0'].iloc[0] = 'abcd1234' # this cannot be casted to float32
    
    df.to_csv(f1.name, index=False)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)
    input_data = DataSource(type_='file', path=inputs_path, ext='.csv')
    label_data = DataSource(type_='file', path=labels_path, ext='.npy')    
    
    builder = GraphSpecBuilder()

    # Branch 1 (Inputs)
    builder.add_layer('DataData', settings={'id_': '1', 'sources': (input_data,)})
    builder.add_layer('ProcessReshape', settings={'id_': '3', 'shape': (28, 28, 1)})
    builder.add_layer('DeepLearningFC', settings={'id_': '4'})
    builder.add_connection('1', 'output', '3', 'input')
    builder.add_connection('3', 'output', '4', 'input')

    # Branch 2 (Labels)
    builder.add_layer('DataData', settings={'id_': '2', 'sources': (label_data,)})    
    builder.add_layer('ProcessOneHot', settings={'id_': '5'})
    builder.add_connection('2', 'output', '5', 'input')                

    # Merge into Training Layer
    conn1 = LayerConnection(src_id='4', src_var='output', dst_id='6', dst_var='predictions')
    conn2 = LayerConnection(src_id='5', src_var='output', dst_id='6', dst_var='labels')      
    
    builder.add_layer('TrainNormal', settings={
        'id_': '6', 'connection_predictions': conn1, 'connection_labels': conn2
    })
    builder.add_connection_object(conn1)
    builder.add_connection_object(conn2)

    graph_spec = builder.build()
    yield graph_spec

    f1.close()
    f2.close()
    


@pytest.fixture(scope='function')
def graph_spec_pre_datawiz_3d(temp_path_checkpoints):
    n_classes = 10
    n_samples = 30

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.random((n_samples, 28, 28, 3))
    np.save(f1.name, mat)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)


    input_data = DataSource(type_='file', path=inputs_path, ext='.npy')
    label_data = DataSource(type_='file', path=labels_path, ext='.npy')    
    
    builder = GraphSpecBuilder()

    # Branch 1 (Inputs)
    builder.add_layer('DataData', settings={'id_': '1', 'sources': (input_data,)})
    builder.add_layer('ProcessReshape', settings={'id_': '3', 'shape': (2352, 1, 1)})
    builder.add_layer('DeepLearningFC', settings={'id_': '4'})
    builder.add_connection('1', 'output', '3', 'input')
    builder.add_connection('3', 'output', '4', 'input')

    # Branch 2 (Labels)
    builder.add_layer('DataData', settings={'id_': '2', 'sources': (label_data,)})    
    builder.add_layer('ProcessOneHot', settings={'id_': '5'})
    builder.add_connection('2', 'output', '5', 'input')                

    # Merge into Training Layer
    conn1 = LayerConnection(src_id='4', src_var='output', dst_id='6', dst_var='predictions')
    conn2 = LayerConnection(src_id='5', src_var='output', dst_id='6', dst_var='labels')      
    
    builder.add_layer('TrainNormal', settings={
        'id_': '6', 'connection_predictions': conn1, 'connection_labels': conn2
    })
    builder.add_connection_object(conn1)
    builder.add_connection_object(conn2)

    graph_spec = builder.build()
    yield graph_spec


    f1.close()
    f2.close()


def test_out_shapes_ok_basic(graph_spec_pre_datawiz):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_pre_datawiz)

    assert results['1'].out_shape['output'] == (784,) # Datadata inputs
    assert results['2'].out_shape['output'] == (1,) # Datadata labels
    assert results['3'].out_shape['output'] == (28, 28, 1) # Reshape
    assert results['4'].out_shape['output'] == (10,) # FC
    assert results['5'].out_shape['output'] == (10,) # One hot
    assert results['6'].out_shape['output'] == (1,)

    
def test_columns_ok_lw(graph_spec_pre_datawiz):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_pre_datawiz)

    assert results['1'].columns == [f'col_{x}' for x in range(784)]

    
def test_columns_ok_when_some_columns_are_strings(graph_spec_pre_datawiz_with_strings):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_pre_datawiz_with_strings)

    assert "ValueError" in results['1'].strategy_error.message # make sure the layer failed in part    
    assert results['1'].columns == [f'col_{x}' for x in range(len(results['1'].columns))]


def test_variables_are_present(graph_spec_pre_datawiz):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_pre_datawiz)


    assert len(results['1'].variables) > 0 # data layer has vars
    assert len(results['4'].variables) > 0 # fc layer has vars   

    
def test_out_shapes_ok_for_3d_samples(graph_spec_pre_datawiz_3d):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_pre_datawiz_3d)
 
    assert results['1'].out_shape['output'] == (28, 28, 3) # Datadata inputs
    assert results['2'].out_shape['output'] == (1,) # Datadata labels
    assert results['3'].out_shape['output'] == (2352, 1, 1) # Reshape
    assert results['4'].out_shape['output'] == (10,) # FC
    assert results['5'].out_shape['output'] == (10,) # One hot
    assert results['6'].out_shape['output'] == (1,) # Train normal


def test_out_shapes_ok_partial_pre_datawiz_graph(graph_spec_partial_pre_datawiz):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_partial_pre_datawiz)
 
    assert results['1'].out_shape['output'] == (784,) # Datadata inputs
    assert '2' not in results # Datadata labels
    assert results['3'].out_shape['output'] == (28, 28, 1) # Reshape
    assert results['4'].out_shape['output'] == (10,) # FC
    assert results['5'].out_shape == {} # One hot
    assert results['6'].out_shape['output'] == None # Train normal
    

def test_out_shapes_ok_with_syntax_error(graph_spec_syntax_error):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_syntax_error)
 
    assert results['1'].out_shape['output'] == (784,) # Datadata inputs
    assert results['2'].out_shape['output'] == (1,) # Datadata labels
    assert results['3'].out_shape == {} # Reshape
    assert results['4'].out_shape == {} # FC
    assert results['5'].out_shape['output'] == (10,) # One hot
    assert results['6'].out_shape['output'] == None  # Train normal


def test_errors_ok_with_syntax_error(graph_spec_syntax_error):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_syntax_error)

    assert "SyntaxError" in results['3'].code_error.message


def test_out_shapes_ok_with_runtime_error(graph_spec_runtime_error):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_runtime_error)
 
    assert results['1'].out_shape['output'] == (784,) # Datadata inputs
    assert results['2'].out_shape['output'] == (1,) # Datadata labels
    assert results['3'].out_shape == {} # Reshape
    assert results['4'].out_shape == {} # FC
    assert results['5'].out_shape['output'] == (10,) # One hot
    assert results['6'].out_shape['output'] == None


def test_errors_ok_with_runtime_error(graph_spec_runtime_error):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_runtime_error)

    assert "ZeroDivisionError" in results['3'].instantiation_error.message
    assert results['3'].instantiation_error.line_number == 2

    
def test_errors_detected_in_training_layer(graph_spec_runtime_error_training):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_runtime_error_training)

    assert "ZeroDivisionError" in results['6'].instantiation_error.message        
    assert results['6'].instantiation_error.line_number == 2    

    
def test_load_checkpoints_ok(graph_spec_pre_datawiz):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_pre_datawiz)

    assert results['1'].trained == False
    assert results['2'].trained == False
    assert results['3'].trained == False
    assert results['4'].trained == False
    assert results['5'].trained == False
    assert results['6'].trained == False

    
def test_calls_cache_get_when_cached_entry_exists(graph_spec_pre_datawiz):
    cache = MagicMock()
    cache.__contains__.return_value = True
    
    lw_core = LightweightCore(cache=cache)
    results = lw_core.run(graph_spec_pre_datawiz)

    assert cache.get.call_count > 0

    
def test_calls_cache_put_when_cached_entry_exists(graph_spec_pre_datawiz):
    cache = MagicMock()
    cache.__contains__.return_value = False
    
    lw_core = LightweightCore(cache=cache)
    results = lw_core.run(graph_spec_pre_datawiz)

    assert cache.put.call_count > 0


def test_preview_available_for_input_layer(csv_path, x1):
    input_spec = InputLayerSpec(id_='123', feature_name='x1', file_path=csv_path, datatype='numerical')
    output_spec = OutputLayerSpec(id_='456', feature_name='y1', file_path=csv_path, datatype='numerical')    
    graph_spec = GraphSpec([input_spec, output_spec])    
    lw_core = LightweightCore(data_loader=DataLoader.from_graph_spec(graph_spec))
    results = lw_core.run(graph_spec)
    assert results['123'].sample.get('output') == x1[0]
    

def test_preview_available_for_output_layer(csv_path, y1):
    input_spec = InputLayerSpec(id_='123', feature_name='x1', file_path=csv_path, datatype='numerical')
    output_spec = OutputLayerSpec(id_='456', feature_name='y1', file_path=csv_path, datatype='numerical')    
    graph_spec = GraphSpec([input_spec, output_spec])
    lw_core = LightweightCore(data_loader=DataLoader.from_graph_spec(graph_spec))
    results = lw_core.run(graph_spec)
    assert results['456'].sample.get('output') == y1[0]    
    

def test_io_layer_samples_are_from_the_same_row(csv_path, graph_spec, x1, y1):
    data_loader = DataLoader.from_features(
        {
            'x1': FeatureSpec('numerical', 'input', csv_path),
            'y1': FeatureSpec('numerical', 'output', csv_path)            
        },
        partitions={'training': 4/5, 'validation': 1/5, 'test': 0.0},
        randomized_partitions=True,
    )
    
    lw_core = LightweightCore(data_loader=data_loader)
    results = lw_core.run(graph_spec)

    outputs_match_one_of_the_rows = False
    for x, y in zip(x1, y1):
        print(results['0'].sample['output'], results['2'].sample['output'])
        if x == results['0'].sample['output'] and y == results['2'].sample['output']:
            outputs_match_one_of_the_rows = True             
            break

    assert outputs_match_one_of_the_rows 
    
