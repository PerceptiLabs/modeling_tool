import pytest
import numpy as np
import pandas as pd
import tempfile
import skimage
import os

from script.utils import RunMacroCodeGenerator


@pytest.fixture(scope='module', autouse=True)
def npy_3000x784():
    np.random.seed(0)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.npy') as f:
        mat = np.random.random((3000, 784))
        np.save(f.name, mat)
        yield f.name

        
@pytest.fixture(scope='module', autouse=True)        
def csv_3000x784():
    np.random.seed(123)    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv') as f:
        mat = np.random.random((3000, 784))
        df = pd.DataFrame.from_records(mat, columns=[str(x) for x in range(784)])
        df.to_csv(f.name, index=False)
        yield f.name

        
@pytest.fixture(scope='module', autouse=True)        
def npy_30x784():
    np.random.seed(0)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.npy') as f:
        mat = np.random.random((30, 784))
        np.save(f.name, mat)
        yield f.name

        
@pytest.fixture(scope='module', autouse=True)        
def csv_30x784():
    np.random.seed(123)    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv') as f:
        mat = np.random.random((30, 784))
        df = pd.DataFrame.from_records(mat, columns=[str(x) for x in range(784)])
        df.to_csv(f.name, index=False)
        yield f.name

        
@pytest.fixture(scope='module', autouse=True)
def npy_ordered():
    np.random.seed(456)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.npy') as f:
        mat = np.atleast_2d(np.arange(3000)).reshape(3000, 1)
        np.save(f.name, mat)
        yield f.name

        
@pytest.fixture(scope='module', autouse=True)
def csv_ordered():
    np.random.seed(789)    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv') as f:
        mat = np.atleast_2d(np.arange(3000)).reshape(3000, 1)        
        df = pd.DataFrame.from_records(mat, columns=['1'])
        df.to_csv(f.name, index=False)
        yield f.name

        
@pytest.fixture(scope='module', autouse=True)
def img_5x32x32x3():
    with tempfile.TemporaryDirectory() as dir_path:
        for i in range(5):
            path = os.path.join(dir_path, str(i)+'.png')            
            matrix = (np.ones((32, 32, 3))*0.1*i).astype(np.float32)
            skimage.io.imsave(path, matrix)
        yield dir_path

        
@pytest.fixture(autouse=True)
def globals_():
    import numpy as np
    import pandas as pd
    import dask.array as da
    import dask.dataframe as dd
    import skimage
    import os
    from unittest.mock import MagicMock
    
    api = MagicMock()
    api.cache.__contains__.return_value = False
    
    return {
        'api': api,
        'np': np,
        'pd': pd,
        'da': da,
        'dd': dd,
        'os': os,
        'skimage': skimage
    }


def test_npy_sample_shape_ok(globals_, npy_3000x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_npy', npy_3000x784, '123')
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    shape = next(gen_fn(0, 3000)).shape    
    assert shape == (784,)

    
def test_csv_sample_shape_ok(globals_, csv_3000x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_3000x784, '123', lazy=False)
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    shape = next(gen_fn(0, 3000)).shape
    assert shape == (784,)

    
def test_csv_lazy_sample_shape_ok(globals_, csv_3000x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_3000x784, '123', lazy=True)
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    shape = next(gen_fn(0, 3000)).shape
    assert shape == (784,)

    
def test_npy_dataset_size_ok(globals_, npy_3000x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_npy', npy_3000x784, '123')
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)
    assert locals_['size_123'] == 3000

    
def test_csv_dataset_size_ok(globals_, csv_3000x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_3000x784, '123', lazy=False)

    locals_ = {}
    exec(gen.get_code(), globals_, locals_)
    assert locals_['size_123'] == 3000

    
def test_npy_slice_generator(globals_, npy_ordered):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_npy', npy_ordered, '123')
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    x = next(gen_fn(1000, 3000))
    assert x == 1000

    
def test_npy_slice_generator(globals_, npy_ordered):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_npy', npy_ordered, '123')
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    x = next(gen_fn(1000, 3000))
    assert x == 1000

    
def test_csv_slice_generator(globals_, csv_ordered):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_ordered, '123')
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    x = next(gen_fn(1000, 3000))
    assert x == 1000

    
def test_csv_lazy_slice_generator(globals_, csv_ordered):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_ordered, '123', lazy=True)
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    x = next(gen_fn(1000, 3000))
    assert x == 1000

    
def test_npy_all_data(globals_, npy_3000x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_npy', npy_3000x784, '123')
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    assert len(list(gen_fn(0, 3000))) == 3000

    
def test_csv_all_data(globals_, csv_3000x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_3000x784, '123', lazy=False)
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    assert len(list(gen_fn(0, 3000))) == 3000

    
def test_csv_lazy_all_data_1_partition(globals_, csv_3000x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_3000x784, '123', lazy=True)
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)
    assert globals_['df_123'].npartitions == 1
    gen_fn = locals_['generator_123']
    assert len(list(gen_fn(0, 3000))) == 3000

    
def test_csv_lazy_all_data_2_partition(globals_, csv_3000x784):
    gen = RunMacroCodeGenerator(
        'file_utils.j2', 'load_csv', csv_3000x784, '123', lazy=True, blocksize='32MB'
    )
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)
    assert globals_['df_123'].npartitions == 2
    gen_fn = locals_['generator_123']
    assert len(list(gen_fn(0, 3000))) == 3000

    
def test_img_dir_all_data(globals_, img_5x32x32x3):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_img_dir', img_5x32x32x3, '123', lazy=False)
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    assert len(list(gen_fn(0, 5))) == 5

    
def test_img_dir_slice_generator(globals_, img_5x32x32x3):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_img_dir', img_5x32x32x3, '123', lazy=False)
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    x = next(gen_fn(1, 3))
    target = skimage.io.imread(os.path.join(img_5x32x32x3, '1.png')).astype(np.float32)

    assert np.all(x == target)

    
def test_img_dir_shape_ok(globals_, img_5x32x32x3):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_img_dir', img_5x32x32x3, '123', lazy=False)
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    x = next(gen_fn(0, 5))
    assert x.shape == (32, 32, 3)

    
def test_csv_column_selection(globals_, csv_30x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_30x784,
                                '123', lazy=False, selected_columns=[1, 3])
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    x = next(gen_fn(0, 30))

    matrix = np.loadtxt(csv_30x784, delimiter=',', skiprows=1).astype(np.float32)
    target = np.hstack([matrix[0, 1], matrix[0, 3]])
    assert np.all(x == target)

    
def test_csv_lazy_column_selection(globals_, csv_30x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_30x784,
                                '123', lazy=True, selected_columns=[1, 3])
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    x = next(gen_fn(0, 30))

    matrix = np.loadtxt(csv_30x784, delimiter=',', skiprows=1).astype(np.float32)
    target = np.hstack([matrix[0, 1], matrix[0, 3]])
    assert np.all(x == target)

    
def test_csv_columns_ok(globals_, csv_30x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_30x784,
                                '123', lazy=False)
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)
    assert locals_['columns_123'] == [str(x) for x in range(784)]

    
def test_csv_lazy_columns_ok(globals_, csv_30x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_30x784,
                                '123', lazy=True)
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)
    assert locals_['columns_123'] == [str(x) for x in range(784)]

    
def test_csv_lazy_cache_called(globals_, csv_30x784):
    api = globals_['api']
    api.cache.__contains__.side_effect = [False, True]
    
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_30x784,
                                '123', lazy=True)
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)
    assert locals_['columns_123'] == [str(x) for x in range(784)]
    
    try:
        locals_ = {}    
        exec(gen.get_code(), globals_, locals_)
    except:
        pass # macro will likely fail on second call since the api is a mock
    finally:
        assert api.cache.put.call_count == 1
        assert api.cache.get.call_count == 1    
    
