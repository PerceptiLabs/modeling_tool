import pytest
import numpy as np
import pandas as pd
import tempfile
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
    np.random.seed(0)    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv') as f:
        mat = np.random.random((3000, 784))
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
        
def test_npy_sample_shape_ok(globals_, npy_3000x784):
    sources = [{'type': 'file', 'path': npy_3000x784}]
    partitions = [(70, 20, 10)]
    gen = DataDataCodeGenerator2(sources, partitions, batch_size=16, shuffle=False, layer_id='abc')

    from pprint import pprint
    pprint(gen.get_code())

    locals_ = {}    
    exec(gen.get_code(), globals_, locals_)
    
    import pdb;pdb.set_trace()
