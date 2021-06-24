import pytest
import numpy as np
import pandas as pd
import tempfile
import os
import skimage
from skimage import io
import pkg_resources

from perceptilabs.script import ScriptFactory
from perceptilabs.core_new.layers.templates.base import J2Engine
from perceptilabs.core_new.layers.templates.utils import instantiate_layer_from_macro, create_layer
from perceptilabs.core_new.layers.definitions import TEMPLATES_DIRECTORY, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT

from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.datadata.spec import DataDataSpec, DataSource



def fix_path(x):
    return x.replace('\\', '/')


@pytest.fixture(scope='module')
def script_factory():
    return ScriptFactory()

@pytest.fixture(scope='module')
def j2_engine():
    templates_directory = pkg_resources.resource_filename('perceptilabs', TEMPLATES_DIRECTORY)    
    j2_engine = J2Engine(templates_directory)
    yield j2_engine

    
@pytest.fixture(scope='module', autouse=True)
def npy_3000x784():
    np.random.seed(0)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False) as f:
        mat = np.random.random((3000, 784))
        np.save(f.name, mat)
        yield fix_path(f.name)
        f.close()

        
@pytest.fixture(scope='module', autouse=True)        
def csv_3000x784():
    np.random.seed(789)    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        mat = np.random.random((3000, 784))
        df = pd.DataFrame.from_records(mat, columns=['col_'+str(x) for x in range(784)])
        df.to_csv(f.name, index=False)
        yield fix_path(f.name)
        f.close()

        
@pytest.fixture(scope='module', autouse=True)
def npy_30x784():
    np.random.seed(123)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False) as f:
        mat = np.random.random((30, 784))
        np.save(f.name, mat)
        yield fix_path(f.name)
        f.close()


@pytest.fixture(scope='module', autouse=True)
def npy_30x28x28():
    np.random.seed(123)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False) as f:
        mat = np.random.random((30, 28, 28))
        np.save(f.name, mat)
        yield fix_path(f.name)
        f.close()

        
@pytest.fixture(scope='module', autouse=True)
def npy_30x28x28x3():
    np.random.seed(123)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False) as f:
        mat = np.random.random((30, 28, 28, 3))
        np.save(f.name, mat)
        yield fix_path(f.name)
        f.close()
        
        
@pytest.fixture(scope='module', autouse=True)
def csv_30x784():
    np.random.seed(456)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        mat = np.random.random((30, 784))
        df = pd.DataFrame.from_records(mat, columns=['col_'+str(x) for x in range(784)])        
        df.to_csv(f.name, index=False)
        yield fix_path(f.name)
        f.close()

        
@pytest.fixture(scope='module', autouse=True)
def img_5x32x32x3():
    with tempfile.TemporaryDirectory() as dir_path:
        for i in range(5):
            path = os.path.join(dir_path, str(i)+'.png')            
            matrix = (np.ones((32, 32, 3))*0.1*i).astype(np.float32)
            skimage.io.imsave(path, matrix)
        yield fix_path(dir_path)


@pytest.mark.skip        
def test_npy_shape_1d_ok(script_factory, npy_30x784):
    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=npy_30x784, ext='.npy', split=(70, 20, 10)),)
    )

    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    assert layer.sample['output'].shape == (784,)


@pytest.mark.skip    
def test_npy_shape_2d_ok(script_factory, npy_30x28x28):
    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=npy_30x28x28, ext='.npy', split=(70, 20, 10)),)
    )

    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    assert layer.sample['output'].shape == (28, 28)
    

@pytest.mark.skip    
def test_npy_shape_3d_ok(script_factory, npy_30x28x28x3):
    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=npy_30x28x28x3, ext='.npy', split=(70, 20, 10)),)
    )
    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()
    assert layer.sample['output'].shape == (28, 28, 3)


@pytest.mark.skip    
def test_csv_shape_ok(script_factory, csv_30x784):
    sources = [{'type': 'file', 'path': csv_30x784, 'ext': '.csv'}]

    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=csv_30x784, ext='.csv', split=(70, 20, 10)),)
    )

    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    assert layer.sample['output'].shape == (784,)


@pytest.mark.skip    
def test_csv_columns_ok(script_factory, csv_30x784):
    sources = [{'type': 'file', 'path': csv_30x784, 'ext': '.csv'}]

    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=csv_30x784, ext='.csv', split=(70, 20, 10)),)
    )

    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    expected_columns = ['col_' + str(x) for x in range(784)]
    assert layer.columns == expected_columns

    
def test_csv_columns_ok_lazy(script_factory, csv_30x784):
    sources = [{'type': 'file', 'path': csv_30x784, 'ext': '.csv'}]

    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=csv_30x784, ext='.csv', split=(70, 20, 10)),),
        lazy=True
    )

    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    expected_columns = ['col_' + str(x) for x in range(784)]
    assert layer.columns == expected_columns


@pytest.mark.skip    
def test_csv_columns_ok_when_selected(script_factory, csv_30x784):
    sources = [{'type': 'file', 'path': csv_30x784, 'ext': '.csv'}]
    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=csv_30x784, ext='.csv', split=(70, 20, 10)),),
        selected_columns=(0, 1)
    )

    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    expected_columns = ['col_' + str(x) for x in range(784)]
    assert layer.sample['output'].shape == (2,)    

@pytest.mark.skip
def test_csv_columns_ok_when_selected_lazy(script_factory, csv_30x784):
    sources = [{'type': 'file', 'path': csv_30x784, 'ext': '.csv'}]

    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=csv_30x784, ext='.csv', split=(70, 20, 10)),),
        selected_columns=(0, 1),
        lazy=True
    )

    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    expected_columns = ['col_' + str(x) for x in range(784)]
    assert layer.sample['output'].shape == (2,)    


@pytest.mark.skip    
def test_npy_shape_1d_ok_lazy(script_factory, npy_30x784):
    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=npy_30x784, ext='.npy', split=(70, 20, 10)),),
        lazy=True
    )

    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    assert layer.sample['output'].shape == (784,)


@pytest.mark.skip    
def test_npy_shape_2d_ok_lazy(script_factory, npy_30x28x28):
    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=npy_30x28x28, ext='.npy', split=(70, 20, 10)),),
        lazy=True
    )

    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    assert layer.sample['output'].shape == (28, 28)
    
@pytest.mark.skip
def test_npy_shape_3d_ok_lazy(script_factory, npy_30x28x28x3):
    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=npy_30x28x28x3, ext='.npy', split=(70, 20, 10)),),
        lazy=True
    )
    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()
    assert layer.sample['output'].shape == (28, 28, 3)


@pytest.mark.skip    
def test_csv_shape_ok_lazy(script_factory, csv_30x784):
    sources = [{'type': 'file', 'path': csv_30x784, 'ext': '.csv'}]

    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=csv_30x784, ext='.csv', split=(70, 20, 10)),),
        lazy=True
    )

    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    assert layer.sample['output'].shape == (784,)


@pytest.mark.skip    
def test_npy_samples_appear_in_order(script_factory, npy_30x784):
    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=npy_30x784, ext='.npy', split=(70, 20, 10)),)
    )
    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    x_trn = np.array([
        x['output']
        for x in layer.make_generator_training()
    ])
    x_val = np.array([
        x['output']
        for x in layer.make_generator_validation()
    ])
    x_tst = np.array([
        x['output']
        for x in layer.make_generator_testing()
    ])
    x = np.vstack([x_trn, x_val, x_tst]) 


    x_ = np.load(npy_30x784).astype(np.float32)
    assert np.all(x == x_)


@pytest.mark.skip        
def test_csv_samples_appear_in_order(script_factory, csv_30x784):
    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=csv_30x784, ext='.csv', split=(70, 20, 10)),)
    )
    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    x_trn = np.array([
        x['output']
        for x in layer.make_generator_training()
    ])
    x_val = np.array([
        x['output']
        for x in layer.make_generator_validation()
    ])
    x_tst = np.array([
        x['output']
        for x in layer.make_generator_testing()
    ])
    x = np.vstack([x_trn, x_val, x_tst]) 

    x_ = np.loadtxt(csv_30x784, delimiter=',', skiprows=1).astype(np.float32)  
    assert np.all(x == x_)
    

@pytest.mark.skip        
def test_npy_and_csv_samples_appear_interleaved(script_factory, npy_30x784, csv_30x784):
    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(
            DataSource(type_='file', path=npy_30x784, ext='.npy', split=(70, 20, 10)),
            DataSource(type_='file', path=csv_30x784, ext='.csv', split=(70, 20, 10)),            
        )
    )
    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    x_trn = np.array([
        x['output']
        for x in layer.make_generator_training()
    ])
    x_val = np.array([
        x['output']
        for x in layer.make_generator_validation()
    ])
    x_tst = np.array([
        x['output']
        for x in layer.make_generator_testing()
    ])
    x = np.vstack([x_trn, x_val, x_tst]) 

    
    mat1 = np.load(npy_30x784).astype(np.float32)
    mat2 = np.loadtxt(csv_30x784, delimiter=',', skiprows=1).astype(np.float32)    

    assert np.all(x_trn[0:21]  == mat1[0:21])
    assert np.all(x_trn[21:42] == mat2[0:21])
    
    assert np.all(x_val[0:6]  == mat1[21:27])
    assert np.all(x_val[6:12] == mat2[21:27])    

    assert np.all(x_tst[0:3] == mat1[27:30])
    assert np.all(x_tst[3:6] == mat2[27:30])    


@pytest.mark.skip        
def test_npy_samples_appear_in_order_lazy(script_factory, npy_30x784):
    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=npy_30x784, ext='.npy', split=(70, 20, 10)),),
        lazy=True
    )
    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    x_trn = np.array([
        x['output']
        for x in layer.make_generator_training()
    ])
    x_val = np.array([
        x['output']
        for x in layer.make_generator_validation()
    ])
    x_tst = np.array([
        x['output']
        for x in layer.make_generator_testing()
    ])
    x = np.vstack([x_trn, x_val, x_tst]) 


    x_ = np.load(npy_30x784).astype(np.float32)
    assert np.all(x == x_)


@pytest.mark.skip        
def test_csv_samples_appear_in_order_lazy(script_factory, csv_30x784):
    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(DataSource(type_='file', path=csv_30x784, ext='.csv', split=(70, 20, 10)),),
        lazy=True
    )
    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    x_trn = np.array([
        x['output']
        for x in layer.make_generator_training()
    ])
    x_val = np.array([
        x['output']
        for x in layer.make_generator_validation()
    ])
    x_tst = np.array([
        x['output']
        for x in layer.make_generator_testing()
    ])
    x = np.vstack([x_trn, x_val, x_tst]) 

    x_ = np.loadtxt(csv_30x784, delimiter=',', skiprows=1).astype(np.float32)      
    assert np.all(x == x_)
    

@pytest.mark.skip        
def test_npy_and_csv_samples_appear_interleaved_lazy(script_factory, npy_30x784, csv_30x784):
    layer_spec = DataDataSpec(
        id_='123', name='layer123', type_='DataData', 
        sources=(
            DataSource(type_='file', path=npy_30x784, ext='.npy', split=(70, 20, 10)),
            DataSource(type_='file', path=csv_30x784, ext='.csv', split=(70, 20, 10)),            
        ),
        lazy=True
    )
    helper = LayerHelper(script_factory, layer_spec)
    layer = helper.get_instance()

    x_trn = np.array([
        x['output']
        for x in layer.make_generator_training()
    ])
    x_val = np.array([
        x['output']
        for x in layer.make_generator_validation()
    ])
    x_tst = np.array([
        x['output']
        for x in layer.make_generator_testing()
    ])
    x = np.vstack([x_trn, x_val, x_tst]) 

    
    mat1 = np.load(npy_30x784).astype(np.float32)
    mat2 = np.loadtxt(csv_30x784, delimiter=',', skiprows=1).astype(np.float32)    

    assert np.all(x_trn[0:21]  == mat1[0:21])
    assert np.all(x_trn[21:42] == mat2[0:21])
    
    assert np.all(x_val[0:6]  == mat1[21:27])
    assert np.all(x_val[6:12] == mat2[21:27])    

    assert np.all(x_tst[0:3] == mat1[27:30])
    assert np.all(x_tst[3:6] == mat2[27:30])    
