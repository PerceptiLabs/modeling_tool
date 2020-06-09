import pytest
import numpy as np
import pandas as pd
import tempfile
import skimage
import os
import pkg_resources

from perceptilabs.core_new.layers.templates.base import J2Engine
from perceptilabs.core_new.layers.definitions import TOP_LEVEL_IMPORTS_FLAT, TEMPLATES_DIRECTORY
from perceptilabs.core_new.layers.templates.utils import render_and_execute_macro


@pytest.fixture(scope='module', autouse=True)
def npy_3000x784():
    np.random.seed(0)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False) as f:
        mat = np.random.random((3000, 784))
        np.save(f.name, mat)
        yield f.name
        f.close()

        
@pytest.fixture(scope='module', autouse=True)        
def csv_3000x784():
    np.random.seed(123)    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        mat = np.random.random((3000, 784))
        df = pd.DataFrame.from_records(mat, columns=[str(x) for x in range(784)])
        df.to_csv(f.name, index=False)
        yield f.name
        f.close()

        
@pytest.fixture(scope='module', autouse=True)        
def npy_30x784():
    np.random.seed(0)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False) as f:
        mat = np.random.random((30, 784))
        np.save(f.name, mat)
        yield f.name
        f.close()

        
@pytest.fixture(scope='module', autouse=True)        
def csv_30x784():
    np.random.seed(123)    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        mat = np.random.random((30, 784))
        df = pd.DataFrame.from_records(mat, columns=[str(x) for x in range(784)])
        df.to_csv(f.name, index=False)
        yield f.name
        f.close()

        
@pytest.fixture(scope='module', autouse=True)
def npy_ordered():
    np.random.seed(456)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False) as f:
        mat = np.atleast_2d(np.arange(3000)).reshape(3000, 1)
        np.save(f.name, mat)
        yield f.name
        f.close()

        
@pytest.fixture(scope='module', autouse=True)
def csv_ordered():
    np.random.seed(789)    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        mat = np.atleast_2d(np.arange(3000)).reshape(3000, 1)        
        df = pd.DataFrame.from_records(mat, columns=['1'])
        df.to_csv(f.name, index=False)
        yield f.name
        f.close()

        
@pytest.fixture(scope='module', autouse=True)
def img_5x32x32x3():
    with tempfile.TemporaryDirectory() as dir_path:
        for i in range(5):
            path = os.path.join(dir_path, str(i)+'.png')            
            matrix = (np.ones((32, 32, 3))*0.1*i).astype(np.float32)
            skimage.io.imsave(path, matrix)
        yield dir_path


@pytest.fixture(scope='module')
def run_macro():
    templates_directory = pkg_resources.resource_filename('perceptilabs', TEMPLATES_DIRECTORY)    
    j2_engine = J2Engine(templates_directory)

    other_imports = [
        'import numpy as np',
        'import pandas as pd',
        'import dask.array as da',
        'import dask.dataframe as dd',
        'import os',
        'import skimage',
        'import multiprocessing'
    ]
                 
    def closure(macro_name, macro_parameters=None):
        module, code = render_and_execute_macro(
            j2_engine,
            'file_utils.j2',
            macro_name,
            macro_parameters=macro_parameters,
            import_statements=TOP_LEVEL_IMPORTS_FLAT + other_imports
        )
        return module, code
    
    yield closure

    
def test_npy_sample_shape_ok(run_macro, npy_3000x784):
    module, _ = run_macro('load_npy', macro_parameters={'path': npy_3000x784, 'tag': '123'})

    shape = next(module.generator_123(0, 3000)).shape    
    assert shape == (784,)

    
def test_csv_sample_shape_ok(run_macro, csv_3000x784):
    module, _ = run_macro('load_csv', macro_parameters={'path': csv_3000x784, 'tag': '123', 'lazy': False})

    shape = next(module.generator_123(0, 3000)).shape
    assert shape == (784,)

    
def test_csv_lazy_sample_shape_ok(run_macro, csv_3000x784):
    module, _ = run_macro('load_csv', macro_parameters={'path': csv_3000x784, 'tag': '123', 'lazy': True})
    shape = next(module.generator_123(0, 3000)).shape
    assert shape == (784,)

    
def test_npy_dataset_size_ok(run_macro, npy_3000x784):
    module, _ = run_macro('load_npy', macro_parameters={'path': npy_3000x784, 'tag': '123'})
    assert module.size_123 == 3000

    
def test_csv_dataset_size_ok(run_macro, csv_3000x784):
    module, _ = run_macro('load_csv', macro_parameters={'path': csv_3000x784, 'tag': '123', 'lazy': False})
    assert module.size_123 == 3000
    
def test_npy_slice_generator(run_macro, npy_ordered):
    module, _ = run_macro('load_npy', macro_parameters={'path': npy_ordered, 'tag': '123'})
    x = next(module.generator_123(1000, 3000))
    assert x == 1000

    
def test_npy_slice_generator(run_macro, npy_ordered):
    module, _ = run_macro('load_npy', macro_parameters={'path': npy_ordered, 'tag': '123'})
    x = next(module.generator_123(1000, 3000))
    assert x == 1000

    
def test_csv_slice_generator(run_macro, csv_ordered):
    module, _ = run_macro('load_csv', macro_parameters={'path': csv_ordered, 'tag': '123'})
    x = next(module.generator_123(1000, 3000))
    assert x == 1000

    
def test_csv_lazy_slice_generator(run_macro, csv_ordered):
    module, _ = run_macro('load_csv', macro_parameters={'path': csv_ordered, 'tag': '123', 'lazy': True})
    x = next(module.generator_123(1000, 3000))
    assert x == 1000

    
def test_npy_all_data(run_macro, npy_3000x784):
    module, _ = run_macro('load_npy', macro_parameters={'path': npy_3000x784, 'tag': '123'})
    assert len(list(module.generator_123(0, 3000))) == 3000

    
def test_csv_all_data(run_macro, csv_3000x784):
    module, _ = run_macro('load_csv', macro_parameters={'path': csv_3000x784, 'tag': '123', 'lazy': False})
    assert len(list(module.generator_123(0, 3000))) == 3000

    
def test_csv_lazy_all_data_1_partition(run_macro, csv_3000x784):
    module, _ = run_macro('load_csv', macro_parameters={'path': csv_3000x784, 'tag': '123', 'lazy': True})
    assert module.df_123.npartitions == 1
    assert len(list(module.generator_123(0, 3000))) == 3000

    
def test_csv_lazy_all_data_2_partition(run_macro, csv_3000x784):
    module, _ = run_macro('load_csv', macro_parameters={'path': csv_3000x784, 'tag': '123', 'lazy': True, 'blocksize': '32MB'})
    
    assert module.df_123.npartitions == 2
    assert len(list(module.generator_123(0, 3000))) == 3000

    
def test_img_dir_all_data(run_macro, img_5x32x32x3):
    module, _ = run_macro('load_img_dir', macro_parameters={'path': img_5x32x32x3, 'tag': '123', 'lazy': False})
    assert len(list(module.generator_123(0, 5))) == 5

    
def test_img_dir_slice_generator(run_macro, img_5x32x32x3):
    module, _ = run_macro('load_img_dir', macro_parameters={'path': img_5x32x32x3, 'tag': '123', 'lazy': False})
    x = next(module.generator_123(1, 3))
    target = skimage.io.imread(os.path.join(img_5x32x32x3, '1.png')).astype(np.float32)
    assert np.all(x == target)

    
def test_img_dir_shape_ok(run_macro, img_5x32x32x3):
    module, _ = run_macro('load_img_dir', macro_parameters={'path': img_5x32x32x3, 'tag': '123', 'lazy': False})
    x = next(module.generator_123(0, 5))
    assert x.shape == (32, 32, 3)

    
def test_csv_column_selection(run_macro, csv_30x784):
    module, _ = run_macro('load_csv', macro_parameters={'path': csv_30x784, 'tag': '123', 'lazy': False, 'selected_columns': [1, 3]})
    x = next(module.generator_123(0, 30))

    matrix = np.loadtxt(csv_30x784, delimiter=',', skiprows=1).astype(np.float32)
    target = np.hstack([matrix[0, 1], matrix[0, 3]])
    assert np.all(x == target)

    
def test_csv_lazy_column_selection(run_macro, csv_30x784):
    module, _ = run_macro('load_csv', macro_parameters={'path': csv_30x784, 'tag': '123', 'lazy': True, 'selected_columns': [1, 3]})

    gen_fn = module.generator_123
    x = next(gen_fn(0, 30))

    matrix = np.loadtxt(csv_30x784, delimiter=',', skiprows=1).astype(np.float32)
    target = np.hstack([matrix[0, 1], matrix[0, 3]])
    assert np.all(x == target)

    
def test_csv_columns_ok(run_macro, csv_30x784):
    module, _ = run_macro('load_csv', macro_parameters={'path': csv_30x784, 'tag': '123', 'lazy': False})
    assert module.columns_123 == [str(x) for x in range(784)]

    
def test_csv_lazy_columns_ok(run_macro, csv_30x784):
    module, _ = run_macro('load_csv', macro_parameters={'path': csv_30x784, 'tag': '123', 'lazy': True})
    assert module.columns_123 == [str(x) for x in range(784)]

    
