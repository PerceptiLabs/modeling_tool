import pytest
import numpy as np
import pandas as pd
import tempfile
import tensorflow as tf
import os

from code_generator.datadata import DataDataCodeGenerator2

@pytest.fixture(scope='module', autouse=True)
def npy_3000x784():
    np.random.seed(0)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.npy') as f:
        mat = np.random.random((3000, 784))
        np.save(f.name, mat)
        yield f.name

@pytest.fixture(scope='module', autouse=True)        
def csv_3000x784():
    np.random.seed(789)    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv') as f:
        mat = np.random.random((3000, 784))
        df = pd.DataFrame.from_records(mat, columns=[str(x) for x in range(784)])
        df.to_csv(f.name, index=False)
        yield f.name

@pytest.fixture(scope='module', autouse=True)
def npy_30x784():
    np.random.seed(123)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.npy') as f:
        mat = np.random.random((30, 784))
        np.save(f.name, mat)
        yield f.name

@pytest.fixture(scope='module', autouse=True)
def csv_30x784():
    np.random.seed(456)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv') as f:
        mat = np.random.random((30, 784))
        df = pd.DataFrame.from_records(mat, columns=[str(x) for x in range(784)])
        df.to_csv(f.name, index=False)
        yield f.name

@pytest.fixture(scope='module', autouse=True)
def globals_():
    import numpy as np
    import pandas as pd
    import dask.array as da
    import dask.dataframe as dd
    import tensorflow as tf
    import itertools
    
    return {
        'np': np,
        'pd': pd,
        'da': da,
        'dd': dd,
        'tf': tf,
        'itertools': itertools
    }

def test_bad_partition(globals_, npy_3000x784):
    sources = [{'type': 'file', 'path': npy_3000x784}]
    partitions = [(1, 2, 3)]

    with pytest.raises(ValueError):
        gen = DataDataCodeGenerator2(sources, partitions, batch_size=16, shuffle=False)

def test_ok_partition(globals_, npy_3000x784):
    sources = [{'type': 'file', 'path': npy_3000x784}]
    partitions = [(70, 20, 10)]
        
    try:
        gen = DataDataCodeGenerator2(sources, partitions, batch_size=16, shuffle=False)        
    except ValueError:
        pytest.fail("Unexpected ValueError!")
        
def test_npy_row_shape_ok(globals_, npy_3000x784):
    batch_size = 16
    sources = [{'type': 'file', 'path': npy_3000x784}]
    partitions = [(70, 20, 10)]
    gen = DataDataCodeGenerator2(sources, partitions, batch_size=batch_size,
                                 shuffle=False, layer_id='abc')
    
    locals_ = {}    
    exec(gen.get_code(), globals_, locals_)

    init = locals_['trn_init']    
    Y = locals_['Y']

    sess = tf.Session()
    sess.run(init)
    y = sess.run(Y)

    assert y.shape == (batch_size, 784)

def test_npy_rows_appear_in_order(globals_, npy_30x784):
    batch_size = 16
    sources = [{'type': 'file', 'path': npy_30x784}]
    partitions = [(70, 20, 10)]
    gen = DataDataCodeGenerator2(sources, partitions, batch_size=batch_size,
                                 shuffle=False, layer_id='abc')
    locals_ = {}    
    exec(gen.get_code(), globals_, locals_)

    sess = tf.Session()

    def get_rows(initializer):
        sess.run(initializer)        
        rows = []
        try:
            while True:
                y = sess.run(locals_['Y'])
                rows.append(y)
        except tf.errors.OutOfRangeError:
            pass
        return np.vstack(rows)

    trn_rows = get_rows(locals_['trn_init'])
    val_rows = get_rows(locals_['val_init'])
    tst_rows = get_rows(locals_['tst_init'])
    all_rows = np.vstack([trn_rows, val_rows, tst_rows])

    target_rows = np.load(npy_30x784).astype(np.float32)
    assert np.all(all_rows == target_rows)

def test_sample_size_ok(globals_, npy_30x784):
    batch_size = 16
    sources = [{'type': 'file', 'path': npy_30x784}]
    partitions = [(70, 20, 10)]
    gen = DataDataCodeGenerator2(sources, partitions, batch_size=batch_size,
                                 shuffle=False, layer_id='abc')
    locals_ = {}    
    exec(gen.get_code(), globals_, locals_)

    assert locals_['_sample'].shape == (784,)

def test_rows_appear_in_order_two_datasets(globals_, npy_30x784, csv_30x784):    
    batch_size = 16
    sources1 = [{'type': 'file', 'path': npy_30x784}]
    partitions1 = [(70, 20, 10)]
    gen1 = DataDataCodeGenerator2(sources1, partitions1, batch_size=batch_size,
                                 shuffle=False, layer_id='abc')
    locals_1 = {}    
    exec(gen1.get_code(), globals_, locals_1)

    sources2 = [{'type': 'file', 'path': csv_30x784}]
    partitions2 = [(70, 20, 10)]
    gen2 = DataDataCodeGenerator2(sources2, partitions2, batch_size=batch_size,
                                 shuffle=False, layer_id='xyz')
    locals_2 = {}    
    exec(gen2.get_code(), globals_, locals_2)

    sess = tf.Session()

    def get_rows(initializer, y_tensor):
        sess.run(initializer)        
        rows = []
        try:
            while True:
                y = sess.run(y_tensor)
                rows.append(y)
        except tf.errors.OutOfRangeError:
            pass
        return np.vstack(rows)

    trn_rows1 = get_rows(locals_1['trn_init'], locals_1['Y'])
    val_rows1 = get_rows(locals_1['val_init'], locals_1['Y'])
    tst_rows1 = get_rows(locals_1['tst_init'], locals_1['Y'])
    all_rows1 = np.vstack([trn_rows1, val_rows1, tst_rows1])
    target_rows1 = np.load(npy_30x784).astype(np.float32)
    
    trn_rows2 = get_rows(locals_2['trn_init'], locals_2['Y'])
    val_rows2 = get_rows(locals_2['val_init'], locals_2['Y'])
    tst_rows2 = get_rows(locals_2['tst_init'], locals_2['Y'])
    all_rows2 = np.vstack([trn_rows2, val_rows2, tst_rows2])
    target_rows2 = np.loadtxt(csv_30x784, delimiter=',', skiprows=1).astype(np.float32)
    
    assert np.all(all_rows2 == target_rows2)
    assert np.all(all_rows1 == target_rows1)


