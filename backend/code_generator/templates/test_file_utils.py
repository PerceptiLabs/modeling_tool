import pytest
import numpy as np
import pandas as pd
import tempfile
import os

from code_generator.utils import RunMacroCodeGenerator

@pytest.fixture(scope='module', autouse=True)
def npy_3000x784():
    np.random.seed(0)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.npy') as f:
        mat = np.random.random((3000, 784))
        np.save(f.name, mat)
        yield f.name

@pytest.fixture(scope='module', autouse=True)        
def csv_3000x784():
    np.random.seed(0)    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv') as f:
        mat = np.random.random((3000, 784))
        df = pd.DataFrame.from_records(mat, columns=[str(x) for x in range(784)])
        df.to_csv(f.name, index=False)

        import pdb; pdb.set_trace()
        
        yield f.name


        
@pytest.fixture(scope='module', autouse=True)
def globals_():
    import numpy as np
    import pandas as pd
    import dask.array as da
    import dask.dataframe as dd
    
    return {
        'np': np,
        'pd': pd,
        'da': da,
        'dd': dd
    }

def test_npy_sample_shape_ok(globals_, npy_3000x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_numpy', npy_3000x784, '123')

    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    shape = next(gen_fn()).shape
    
    assert shape == (784,)
    
def test_csv_sample_shape_ok(globals_, csv_3000x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_3000x784, '123', lazy=False)

    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    shape = next(gen_fn()).shape
    
    assert shape == (784,)

def test_csv_lazy_sample_shape_ok(globals_, csv_3000x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_3000x784, '123', lazy=True)
    
    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    gen_fn = locals_['generator_123']
    shape = next(gen_fn()).shape
    
    assert shape == (784,)

def test_npy_dataset_size_ok(globals_, npy_3000x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_numpy', npy_3000x784, '123')

    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    assert locals_['size_123'] == 3000

def test_csv_dataset_size_ok(globals_, csv_3000x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_3000x784, '123', lazy=False)

    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    assert locals_['size_123'] == 3000
    
def test_csv_lazy_dataset_size_ok(globals_, csv_3000x784):
    gen = RunMacroCodeGenerator('file_utils.j2', 'load_csv', csv_3000x784, '123', lazy=True)

    locals_ = {}
    exec(gen.get_code(), globals_, locals_)

    assert locals_['size_123'] == 3000

    
