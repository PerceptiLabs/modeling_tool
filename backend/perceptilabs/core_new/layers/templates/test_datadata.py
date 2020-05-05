import pytest
import numpy as np
import pandas as pd
import tempfile
import os
import skimage
import pkg_resources


from perceptilabs.core_new.layers.templates.base import J2Engine
from perceptilabs.core_new.layers.templates.utils import instantiate_layer_from_macro, create_layer
from perceptilabs.core_new.layers.definitions import TEMPLATES_DIRECTORY, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT


def fix_path(x):
    return x.replace('\\', '/')


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

        
def test_npy_shape_1d_ok(j2_engine, npy_30x784):
    sources = [{'type': 'file', 'path': npy_30x784, 'ext': '.npy'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,        
    )

    assert layer.sample.shape == (784,)


def test_npy_shape_2d_ok(j2_engine, npy_30x28x28):
    sources = [{'type': 'file', 'path': npy_30x28x28, 'ext': '.npy'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,        
    )

    assert layer.sample.shape == (28, 28)
    

def test_npy_shape_3d_ok(j2_engine, npy_30x28x28x3):
    sources = [{'type': 'file', 'path': npy_30x28x28x3, 'ext': '.npy'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,        
    )

    assert layer.sample.shape == (28, 28, 3)


def test_csv_shape_ok(j2_engine, csv_30x784):
    sources = [{'type': 'file', 'path': csv_30x784, 'ext': '.csv'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,
        lazy=False
    )

    assert layer.sample.shape == (784,)
    

def test_csv_columns_ok(j2_engine, csv_30x784):
    sources = [{'type': 'file', 'path': csv_30x784, 'ext': '.csv'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT,
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,
        lazy=False
    )

    expected_columns = ['col_' + str(x) for x in range(784)]
    assert layer.columns == expected_columns

    
def test_csv_columns_ok_lazy(j2_engine, csv_30x784):
    sources = [{'type': 'file', 'path': csv_30x784, 'ext': '.csv'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT,
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,
        lazy=True
    )

    expected_columns = ['col_' + str(x) for x in range(784)]
    assert layer.columns == expected_columns


def test_csv_columns_ok_when_selected(j2_engine, csv_30x784):
    sources = [{'type': 'file', 'path': csv_30x784, 'ext': '.csv'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT,
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=[0, 1],
        lazy=False
    )

    assert layer.sample.shape == (2,)


def test_csv_columns_ok_when_selected_lazy(j2_engine, csv_30x784):
    sources = [{'type': 'file', 'path': csv_30x784, 'ext': '.csv'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT,
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=[0, 1],
        lazy=True
    )

    assert layer.sample.shape == (2,)

    
def test_npy_shape_1d_ok_lazy(j2_engine, npy_30x784):
    sources = [{'type': 'file', 'path': npy_30x784, 'ext': '.npy'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,        
        lazy=True
    )

    assert layer.sample.shape == (784,)


def test_npy_shape_2d_ok_lazy(j2_engine, npy_30x28x28):
    sources = [{'type': 'file', 'path': npy_30x28x28, 'ext': '.npy'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,        
        lazy=True
    )

    assert layer.sample.shape == (28, 28)
    

def test_npy_shape_3d_ok_lazy(j2_engine, npy_30x28x28x3):
    sources = [{'type': 'file', 'path': npy_30x28x28x3, 'ext': '.npy'}]
    partitions = [(70, 20, 10)]
    
    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,        
        lazy=True
    )

    assert layer.sample.shape == (28, 28, 3)


def test_csv_shape_ok_lazy(j2_engine, csv_30x784):
    sources = [{'type': 'file', 'path': csv_30x784, 'ext': '.csv'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,
        lazy=True        
    )

    assert layer.sample.shape == (784,)


def test_npy_samples_appear_in_order(j2_engine, npy_30x784):
    sources = [{'type': 'file', 'path': npy_30x784, 'ext': '.npy'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,
        lazy=False
    )

    x_trn = np.array(list(layer.make_generator_training()))
    x_val = np.array(list(layer.make_generator_validation()))
    x_tst = np.array(list(layer.make_generator_testing()))    
    x = np.vstack([x_trn, x_val, x_tst]) 

    x_ = np.load(npy_30x784).astype(np.float32)
    assert np.all(x == x_)


def test_csv_samples_appear_in_order(j2_engine, csv_30x784):
    sources = [{'type': 'file', 'path': csv_30x784, 'ext': '.csv'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,
        lazy=False
    )

    x_trn = np.array(list(layer.make_generator_training()))
    x_val = np.array(list(layer.make_generator_validation()))
    x_tst = np.array(list(layer.make_generator_testing()))    
    x = np.vstack([x_trn, x_val, x_tst]) 

    x_ = np.loadtxt(csv_30x784, delimiter=',', skiprows=1).astype(np.float32)        
    assert np.all(x == x_)
    

def test_npy_and_csv_samples_appear_interleaved(j2_engine, npy_30x784, csv_30x784):
    sources = [
        {'type': 'file', 'path': npy_30x784, 'ext': '.npy'},
        {'type': 'file', 'path': csv_30x784, 'ext': '.csv'},        
    ]
    partitions = [(70, 20, 10), (70, 20, 10)]
        
    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,
        lazy=False
    )

    x_trn = np.array(list(layer.make_generator_training()))
    x_val = np.array(list(layer.make_generator_validation()))
    x_tst = np.array(list(layer.make_generator_testing()))    
    x = np.vstack([x_trn, x_val, x_tst]) 

    mat1 = np.load(npy_30x784).astype(np.float32)
    mat2 = np.loadtxt(csv_30x784, delimiter=',', skiprows=1).astype(np.float32)    

    assert np.all(x_trn[0:21]  == mat1[0:21])
    assert np.all(x_trn[21:42] == mat2[0:21])
    
    assert np.all(x_val[0:6]  == mat1[21:27])
    assert np.all(x_val[6:12] == mat2[21:27])    

    assert np.all(x_tst[0:3] == mat1[27:30])
    assert np.all(x_tst[3:6] == mat2[27:30])    

    
def test_npy_samples_appear_in_order_lazy(j2_engine, npy_30x784):
    sources = [{'type': 'file', 'path': npy_30x784, 'ext': '.npy'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,
        lazy=True
    )

    x_trn = np.array(list(layer.make_generator_training()))
    x_val = np.array(list(layer.make_generator_validation()))
    x_tst = np.array(list(layer.make_generator_testing()))    
    x = np.vstack([x_trn, x_val, x_tst]) 

    x_ = np.load(npy_30x784).astype(np.float32)
    assert np.all(x == x_)


def test_csv_samples_appear_in_order_lazy(j2_engine, csv_30x784):
    sources = [{'type': 'file', 'path': csv_30x784, 'ext': '.csv'}]
    partitions = [(70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,
        lazy=True
    )

    x_trn = np.array(list(layer.make_generator_training()))
    x_val = np.array(list(layer.make_generator_validation()))
    x_tst = np.array(list(layer.make_generator_testing()))    
    x = np.vstack([x_trn, x_val, x_tst]) 

    x_ = np.loadtxt(csv_30x784, delimiter=',', skiprows=1).astype(np.float32)        
    assert np.all(x == x_)
    

def test_npy_and_csv_samples_appear_interleaved_lazy(j2_engine, npy_30x784, csv_30x784):
    sources = [
        {'type': 'file', 'path': npy_30x784, 'ext': '.npy'},
        {'type': 'file', 'path': csv_30x784, 'ext': '.csv'},        
    ]
    partitions = [(70, 20, 10), (70, 20, 10)]

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        'DataData',
        sources=sources,
        partitions=partitions,
        selected_columns=None,
        lazy=True
    )

    x_trn = np.array(list(layer.make_generator_training()))
    x_val = np.array(list(layer.make_generator_validation()))
    x_tst = np.array(list(layer.make_generator_testing()))    
    x = np.vstack([x_trn, x_val, x_tst]) 

    mat1 = np.load(npy_30x784).astype(np.float32)
    mat2 = np.loadtxt(csv_30x784, delimiter=',', skiprows=1).astype(np.float32)    

    assert np.all(x_trn[0:21]  == mat1[0:21])
    assert np.all(x_trn[21:42] == mat2[0:21])
    
    assert np.all(x_val[0:6]  == mat1[21:27])
    assert np.all(x_val[6:12] == mat2[21:27])    

    assert np.all(x_tst[0:3] == mat1[27:30])
    assert np.all(x_tst[3:6] == mat2[27:30])    
    
