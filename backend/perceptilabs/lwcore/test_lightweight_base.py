import os
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock


from perceptilabs.lwcore import LightweightCore
from perceptilabs.utils import sanitize_path
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.layers.iooutput.spec import OutputLayerSpec
from perceptilabs.layers.ioinput.spec import InputLayerSpec
from perceptilabs.layers.iooutput.spec import OutputLayerSpec
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import FeatureSpec, DatasetSettings, Partitions
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.layers.specbase import LayerConnection
from perceptilabs.data.utils.builder import DatasetBuilder


@pytest.fixture(scope='function')
def data_loader():
    builder = DatasetBuilder.from_features({
        'x': {'datatype': 'image', 'iotype': 'input'},
        'y': {'datatype': 'numerical', 'iotype': 'target'},
    })

    n_samples = 10
    with builder:
        for i in range(n_samples):
            with builder.create_row() as row:
                row.file_data['x'] = np.random.randint(0, 255, (28, 28, 1), dtype=np.uint8)
                row.file_type['x'] = '.png'                      
                row.literals['y'] = i

        data_loader = builder.get_data_loader()
        yield data_loader


@pytest.fixture(scope='function')
def data_loader_3d():
    builder = DatasetBuilder.from_features({
        'x': {'datatype': 'image', 'iotype': 'input'},
        'y': {'datatype': 'numerical', 'iotype': 'target'},
    })

    n_samples = 10
    with builder:
        for i in range(n_samples):
            with builder.create_row() as row:
                row.file_data['x'] = np.random.randint(0, 255, (28, 28, 3), dtype=np.uint8)
                row.file_type['x'] = '.png'                      
                row.literals['y'] = i

        data_loader = builder.get_data_loader()
        yield data_loader

        
@pytest.fixture()
def x1():
    yield [123.0, 24.0, 13.0, 45.0, -10.0]


@pytest.fixture()
def y1():
    yield [1.0, 2.0, 3.0, 4.0, -1.0]


@pytest.fixture()
def df(x1, y1):
    df = pd.DataFrame({'x1': x1, 'y1': y1})
    yield df


@pytest.fixture()
def graph_spec():
    gsb = GraphSpecBuilder()
    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'id_': 'input0', 'datatype': 'image', 'feature_name': 'x'}
    )
    id2 = gsb.add_layer(
        'ProcessReshape',
        settings={'id_': 'reshape0', 'shape': (14, 14, 4)}
    )    
    id3 = gsb.add_layer(
        'DeepLearningFC',
        settings={'id_': 'fc0', 'n_neurons': 1}
    )    
    id4 = gsb.add_layer(
        'IoOutput',
        settings={'id_': 'output0', 'datatype': 'categorical', 'feature_name': 'y'}
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
    gsb.add_connection(
        source_id=id3, source_var='output',
        dest_id=id4, dest_var='input'
    )
    graph_spec = gsb.build()
    return graph_spec


@pytest.fixture()
def graph_spec_partial():
    gsb = GraphSpecBuilder()
    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'id_': 'input0', 'datatype': 'image', 'feature_name': 'x'}
    )
    id2 = gsb.add_layer(
        'ProcessReshape',
        settings={'id_': 'reshape0', 'shape': (14, 14, 4)}
    )    
    id3 = gsb.add_layer(
        'DeepLearningFC',
        settings={'id_': 'fc0', 'n_neurons': 1}
    )
    id4 = gsb.add_layer(
        'DeepLearningFC',
        settings={'id_': 'fc1', 'n_neurons': 1}
    )    
    id5 = gsb.add_layer(
        'IoOutput',
        settings={'id_': 'output0', 'datatype': 'categorical', 'feature_name': 'y'}
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
    gsb.add_connection(
        source_id=id4, source_var='output',
        dest_id=id5, dest_var='input'
    )
    graph_spec = gsb.build()
    return graph_spec


@pytest.fixture()
def graph_spec_3d():
    gsb = GraphSpecBuilder()
    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'id_': 'input0', 'datatype': 'image', 'feature_name': 'x'}
    )
    id2 = gsb.add_layer(
        'ProcessReshape',
        settings={'id_': 'reshape0', 'shape': (14, 14, 12)}
    )    
    id3 = gsb.add_layer(
        'DeepLearningFC',
        settings={'id_': 'fc0', 'n_neurons': 1}
    )    
    id4 = gsb.add_layer(
        'IoOutput',
        settings={'id_': 'output0', 'datatype': 'categorical', 'feature_name': 'y'}
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
    gsb.add_connection(
        source_id=id3, source_var='output',
        dest_id=id4, dest_var='input'
    )
    graph_spec = gsb.build()
    return graph_spec


@pytest.fixture()
def graph_spec_wrong_output_shape():
    gsb = GraphSpecBuilder()
    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'datatype': 'image', 'feature_name': 'x'}
    )
    id2 = gsb.add_layer(
        'DeepLearningFC',
        settings={'n_neurons': 11}
    )
    id3 = gsb.add_layer(
        'IoOutput',
        settings={'datatype': 'numerical', 'feature_name': 'y'}
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



@pytest.fixture()
def graph_spec_runtime_error():
    gsb = GraphSpecBuilder()
    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'datatype': 'image', 'feature_name': 'x'}
    )
    id2 = gsb.add_layer('ProcessReshape', settings={
        'shape': (28, 28, 1),
        'custom_code': "print('hello')\n1/0"  # Causes Runtime error by zero division
    })
    
    id3 = gsb.add_layer(
        'DeepLearningFC',
        settings={'n_neurons': 1}
    )
    id4 = gsb.add_layer(
        'IoOutput',
        settings={'datatype': 'numerical', 'feature_name': 'y'}
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
    gsb.add_connection(
        source_id=id3, source_var='output',
        dest_id=id4, dest_var='input'
    )
    graph_spec = gsb.build()
    return graph_spec




@pytest.fixture(scope='function')
def graph_spec_syntax_error(temp_path_checkpoints):
    gsb = GraphSpecBuilder()
    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'datatype': 'image', 'feature_name': 'x'}
    )
    
    id2 = gsb.add_layer('ProcessReshape', settings={
        'shape': (28, 28, 1),
        'custom_code': "print('hello')\n!!!"  # Causes SyntaxError due to exclamation marks        
    })
    
    id3 = gsb.add_layer(
        'DeepLearningFC',
        settings={'n_neurons': 1}
    )
    id4 = gsb.add_layer(
        'IoOutput',
        settings={'datatype': 'numerical', 'feature_name': 'y'}
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
    gsb.add_connection(
        source_id=id3, source_var='output',
        dest_id=id4, dest_var='input'
    )

    return gsb.build()


def test_out_shapes_ok_basic(data_loader, graph_spec):
    lw_core = LightweightCore(data_loader)
    results = lw_core.run(graph_spec)

    assert results['input0'].out_shape['output'] == (28, 28, 1)
    assert results['reshape0'].out_shape['output'] == (14, 14, 4) 
    assert results['fc0'].out_shape['output'] == (1,) 
    assert results['output0'].out_shape['output'] == (1,)


def test_variables_are_present(data_loader, graph_spec):
    lw_core = LightweightCore(data_loader)
    results = lw_core.run(graph_spec)

    assert results['input0'].variables == {}  
    assert results['output0'].variables == {}
    assert results['reshape0'].variables == {}
    
    assert len(results['fc0'].variables) > 0

    
def test_out_shapes_ok_for_3d_samples(data_loader_3d, graph_spec_3d):
    lw_core = LightweightCore(data_loader_3d)
    results = lw_core.run(graph_spec_3d)

    assert results['input0'].out_shape['output'] == (28, 28, 3)
    assert results['reshape0'].out_shape['output'] == (14, 14, 12) 
    assert results['fc0'].out_shape['output'] == (1,) 
    assert results['output0'].out_shape['output'] == (1,)

    
def test_out_shapes_ok_partial(data_loader, graph_spec_partial):
    lw_core = LightweightCore(data_loader)
    results = lw_core.run(graph_spec_partial)

    assert results['input0'].out_shape['output'] == (28, 28, 1)
    assert results['reshape0'].out_shape['output'] == (14, 14, 4) 
    assert results['fc0'].out_shape['output'] == (1,)
    assert results['fc1'].out_shape == {}
    assert results['output0'].out_shape['output'] == (1,)
    

def test_out_shapes_ok_with_syntax_error(data_loader, graph_spec_syntax_error):
    lw_core = LightweightCore(data_loader)
    results = lw_core.run(graph_spec_syntax_error)

    assert results['0'].out_shape['output'] == (28, 28, 1) # Datadata inputs
    assert results['1'].out_shape == {} # Reshape
    assert results['2'].out_shape == {} # FC
    assert results['3'].out_shape['output'] == (1,)

    
def test_errors_ok_with_syntax_error(data_loader, graph_spec_syntax_error):
    lw_core = LightweightCore(data_loader)
    results = lw_core.run(graph_spec_syntax_error)
    assert "SyntaxError" in results['1'].code_error.message


def test_out_shapes_ok_with_runtime_error(data_loader, graph_spec_runtime_error):
    lw_core = LightweightCore(data_loader)
    results = lw_core.run(graph_spec_runtime_error)

    assert results['0'].out_shape['output'] == (28, 28, 1) # Datadata inputs
    assert results['1'].out_shape == {} # Reshape
    assert results['2'].out_shape == {} # FC
    assert results['3'].out_shape['output'] == (1,)


def test_errors_ok_with_runtime_error(data_loader, graph_spec_runtime_error):
    lw_core = LightweightCore(data_loader)
    results = lw_core.run(graph_spec_runtime_error)

    assert "ZeroDivisionError" in results['1'].instantiation_error.message
    assert results['1'].instantiation_error.line_number == 2


def test_load_checkpoints_ok(data_loader, graph_spec):
    lw_core = LightweightCore(data_loader)
    results = lw_core.run(graph_spec)

    for result in results.values():
        assert not result.trained

        
def test_tries_to_use_cached_value(data_loader, graph_spec):
    cache = MagicMock()
    get_or_calculate = cache.for_compound_keys.return_value.get_or_calculate
    get_or_calculate.return_value = None, True

    lw_core = LightweightCore(data_loader, cache=cache)
    results = lw_core.run(graph_spec)

    assert get_or_calculate.call_count > 0


def test_preview_available_for_input_layer(df, x1):
    input_spec = InputLayerSpec(id_='123', feature_name='x1', datatype='numerical')
    output_spec = OutputLayerSpec(id_='456', feature_name='y1', datatype='numerical')
    feature_specs = {
        'x1': FeatureSpec(iotype='input', datatype='numerical'),
        'y1': FeatureSpec(iotype='target', datatype='numerical')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)

    data_loader = DataLoader(df, dataset_settings)
    lw_core = LightweightCore(data_loader=data_loader)

    graph_spec = GraphSpec([input_spec, output_spec])    
    results = lw_core.run(graph_spec)
    assert results['123'].sample.get('output') == x1[0]


def test_preview_available_for_output_layer(df, y1):
    input_spec = InputLayerSpec(id_='123', feature_name='x1', datatype='numerical')
    output_spec = OutputLayerSpec(id_='456', feature_name='y1', datatype='numerical')
    feature_specs = {
        'x1': FeatureSpec(iotype='input', datatype='numerical'),
        'y1': FeatureSpec(iotype='target', datatype='numerical')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)

    data_loader = DataLoader(df, dataset_settings)
    lw_core = LightweightCore(data_loader=data_loader)

    graph_spec = GraphSpec([input_spec, output_spec])    
    results = lw_core.run(graph_spec)
    assert results['456'].sample.get('output') == y1[0]


def test_io_layer_samples_are_from_the_same_row(data_loader, graph_spec):
    lw_core = LightweightCore(data_loader)
    results = lw_core.run(graph_spec)

    input_preview = results['input0'].sample['output']
    target_preview = results['output0'].sample['output']    

    def previews_match_row_in_dataset(input_preview, target_preview):
        for inputs_batch, targets_batch in data_loader.get_dataset(partition='training'):
            input_value = inputs_batch['x'].numpy()
            target_value = targets_batch['y'].numpy()            
            
            if np.all(input_preview == input_value) and np.all(target_preview == target_value):
                return True

        return False

    assert previews_match_row_in_dataset(input_preview, target_preview)

    
def test_output_layer_raises_error_if_inputs_shape_doesnt_match(data_loader, graph_spec_wrong_output_shape):
    lw_core = LightweightCore(data_loader)
    results = lw_core.run(graph_spec_wrong_output_shape)
    assert results['2'].has_errors



