import csv
import numpy as np
import os
from abc import ABC, abstractmethod

from code_generator import CodeGenerator
from s3buckets import S3BucketAdapter


class AbstractStrategy(ABC):
    @abstractmethod
    def execute(self, var_train, var_valid, var_test, rate_train, rate_valid, rate_test):    
        raise NotImplementedError

    
class FileNumpyStrategy(AbstractStrategy):
    def __init__(self, path):
        self._path = path

    def execute(self, var_train, var_valid, var_test, rate_train, rate_valid, rate_test):
        code  = "if '%s' not in api.cache:\n" % self._path
        code += "    data_mat = np.load('%s').astype(np.float32)\n" % self._path
        code += "    api.cache.put('%s', data_mat)\n" % self._path
        code += "else:\n"
        code += "    data_mat = api.cache.get('%s')\n" % self._path
        code += "data_mat = da.from_array(data_mat)\n"
        code += "%s, %s, %s, %s_size, %s_size, %s_size = split(data_mat, %f, %f, %f)\n" % (var_train, var_valid, var_test,
                                                                                           var_train, var_valid, var_test,
                                                                                           rate_train, rate_valid, rate_test)
        return code

    
class FileCsvStrategy(AbstractStrategy):
    def __init__(self, path, columns):
        self._path = path
        self._columns=columns



    def execute_(self, var_train, var_valid, var_test, rate_train, rate_valid, rate_test):
        # TODO: do not use custom splitting for csvs. this is necessary for lazy generator atm
        code  = 'def split_(array, train_rate, test_rate, validation_rate):\n'
        code += '    def generator(array, idx_from, idx_to):\n'
        code += '        df = dd.from_dask_array(array[idx_from:idx_to])\n'
        code += '        for x in df.iterrows():\n'
        code += '            print("valshape",x[1].values.shape)\n'
        code += '            yield x[1].values.squeeze()\n'
        code += '    \n'
        code += '    array.compute_chunk_sizes()\n'
        code += '    size = len(array)\n'
        code += '    train_size = round(train_rate*size)\n'
        code += '    validation_size = round(validation_rate*size)\n'
        code += '    test_size = size - train_size - validation_size\n'
        code += '    \n'
        code += '    train_gen = generator(array, 0, train_size)\n'
        code += '    validation_gen = generator(array, train_size, train_size+validation_size)        \n'
        code += '    test_gen = generator(array, train_size+validation_size, size)\n'
        code += '    return train_gen, test_gen, validation_gen, train_size, test_size, validation_size\n'
        code += '\n'
        
        code += "if '%s' not in api.cache:\n" % self._path        
        code += "    df = dd.read_csv('%s')\n" % self._path
        code += "    cols = list(df.columns)\n"
        if self._columns:
            code += "    data_mat = df[%s].values.astype(np.float32)\n" % str(["cols[%d]" % i for i in self._columns]).replace("'","")
        else:
            code += "    data_mat = df.values.astype(np.float32)\n"
        code += "    api.cache.put('%s', data_mat)\n" % self._path            
        code += "else:\n"
        code += "    data_mat = api.cache.get('%s')\n" % self._path
        code += "%s, %s, %s, %s_size, %s_size, %s_size = split_(data_mat, %f, %f, %f)\n" % (var_train, var_valid, var_test,
                                                                                           var_train, var_valid, var_test,
                                                                                           rate_train, rate_valid, rate_test)
        #code += "print('SPLIT SIZES!!!', %s_size, %s_size, %s_size)\n" % (var_train, var_valid, var_test)        
        return code

    
    def execute(self, var_train, var_valid, var_test, rate_train, rate_valid, rate_test):

        code  = ""
        code += "df = dd.read_csv('%s', blocksize='100MB')\n" % self._path
        code += "cols = list(df.columns)\n"

        if self._columns:
            code +="df = df[%s]\n" % str(["cols[%d]" % i for i in self._columns]).replace("'","")
        
        code += "df_train, df_validation, df_test = df.random_split([%f, %f, %f])\n" % (rate_train, rate_valid, rate_test)
        code += "\n"
        code += "def generator(df):\n"
        code += "    for x in df.iterrows():\n"
        code += "        y = x[1].values.squeeze()\n"
        #code += "        print('GENERATE', type(y), y.shape, y)\n"
        code += "        yield y\n"
        code += "\n"
        code += "%s = generator(df_train)\n" % var_train
        code += "%s = generator(df_validation)\n" % var_valid
        code += "%s = generator(df_test)\n" % var_test
        code += "\n"
        code += "# The size estimates are only used for visualizations\n"
        code += "size = len(df.partitions[0])*df.npartitions\n"
        #code += "size = len(df)\n"
        code += "%s_size = round(%f*size)\n" % (var_train, rate_train)
        code += "%s_size = round(%f*size)\n" % (var_valid, rate_valid)
        code += "%s_size = size - %s_size - %s_size\n" % (var_test, var_train, var_valid)
        return code        

    
class DirectoryImageStrategy(AbstractStrategy):
    def __init__(self, path):
        self._path = path

    def execute(self, var_train, var_valid, var_test, rate_train, rate_valid, rate_test):
        code = ""
        code += "file_paths = [os.path.join('%s', p)\n" % self._path
        code += "for p in os.listdir('%s')]\n\n" % self._path
        code += "data_mat_list = []\n"
        code += "for path in file_paths:\n"
        code += "    if path not in api.cache:\n"
        code += "        data_mat = skimage.io.imread(path)\n"
        code += "        api.cache.put(path, data_mat)\n"
        code += "    else:\n"
        code += "        data_mat = api.cache.get(path)\n"
        code += "    data_mat_list.append(data_mat)\n"
        code += "\n"
        code += "data_mat = np.array(data_mat_list).astype(np.float32)\n"
        code += "data_mat = da.from_array(data_mat)\n"
        code += "%s, %s, %s, %s_size, %s_size, %s_size = split(data_mat, %f, %f, %f)\n" % (var_train, var_valid, var_test,
                                                                                           var_train, var_valid, var_test,
                                                                                           rate_train, rate_valid, rate_test)
        return code


class FileJsonStrategy(AbstractStrategy):
    def __init__(self, path):
        self._path = path

    def execute(self, var_train, var_valid, var_test, rate_train, rate_valid, rate_test):
        code  = "if '%s' not in api.cache:\n" % self._path
        code += "    with open('%s', 'r') as f:\n" % self._path
        code += "        json_dict = json.load(f)\n"        
        code += "    df = pd.DataFrame.from_dict(json_dict)\n"
        code += "    data_mat = df.to_numpy().astype(np.float32)\n"
        code += "    api.cache.put('%s', data_mat)\n" % self._path
        code += "else:\n"
        code += "    data_mat = api.cache.get('%s')\n" % self._path
        code += "data_mat = da.from_array(data_mat)\n"
        code += "%s, %s, %s, %s_size, %s_size, %s_size = split(data_mat, %f, %f, %f)\n" % (var_train, var_valid, var_test,
                                                                                           var_train, var_valid, var_test,
                                                                                           rate_train, rate_valid, rate_test)
        return code

    
class S3BucketImageStrategy(AbstractStrategy): # TODO: should look into simplifying this using dask
    def __init__(self, bucket, region_name, delimiter, prefix,
                 aws_access_key_id, aws_secret_access_key):
        self._bucket = bucket
        self._region = region_name
        self._delimiter = delimiter
        self._prefix = prefix
        self._aws_key_id = aws_access_key_id
        self._aws_key = aws_secret_access_key        

    def execute(self, var_train, var_valid, var_test, rate_train, rate_valid, rate_test):
        code = ""
        code += "adapter = S3BucketAdapter(bucket='%s',\n" % self._bucket
        code += "                          region_name='%s',\n" % self._region
        code += "                          aws_access_key_id='%s',\n" % self._aws_key_id
        code += "                          aws_secret_access_key='%s')\n" % self._aws_key
        code += "\n"
        code += "file_keys = adapter.get_keys(delimiter='%s',\n" % self._delimiter
        code += "                             prefix='%s')\n" % self._prefix
        code += "data_mat_list = []\n"
        code += "for key in file_keys:\n"
        code += "    if key not in api.cache:\n"
        code += "        file_path = adapter.download_file(key)\n"
        code += "        data_mat = skimage.io.imread(file_path)\n"
        code += "        api.cache.put(path, data_mat)\n"        
        code += "    else:\n"
        code += "        data_mat = api.cache.get(path)\n"
        code += "    data_mat_list.append(data_mat)\n"
        code += "\n"
        code += "adapter.close()\n"                
        code += "data_mat = np.array(data_mat_list).astype(np.float32)\n"
        code += "data_mat = da.from_array(data_mat)\n"
        code += "%s, %s, %s, %s_size, %s_size, %s_size = split(data_mat, %f, %f, %f)\n" % (var_train, var_valid, var_test,
                                                                                           var_train, var_valid, var_test,
                                                                                           rate_train, rate_valid, rate_test)
        return code

    
class S3BucketJsonStrategy(AbstractStrategy):# TODO: should look into simplifying this using dask
    def __init__(self, bucket, region_name, delimiter, prefix,
                 aws_access_key_id, aws_secret_access_key):
        self._bucket = bucket
        self._region = region_name
        self._delimiter = delimiter
        self._prefix = prefix
        self._aws_key_id = aws_access_key_id
        self._aws_key = aws_secret_access_key
        
    def execute(self, var_train, var_valid, var_test, rate_train, rate_valid, rate_test):
        code = ""
        code += "adapter = S3BucketAdapter(bucket='%s',\n" % self._bucket
        code += "                          region_name='%s',\n" % self._region
        code += "                          aws_access_key_id='%s',\n" % self._aws_key_id
        code += "                          aws_secret_access_key='%s')\n" % self._aws_key
        code += "\n"
        code += "file_keys = adapter.get_keys(delimiter='%s',\n" % self._delimiter
        code += "                             prefix='%s')\n" % self._prefix
        code += "data_mat_list = []\n"
        code += "for key in file_keys:\n"
        code += "    if key not in api.cache:\n"        
        code += "        file_path = adapter.download_file(key)\n"
        code += "        with open(file_path, 'r') as f:\n"
        code += "            json_dict = json.load(f)\n"        
        code += "        df = pd.DataFrame.from_dict(json_dict)\n"
        code += "        data_mat = df.to_numpy().astype(np.float32)\n"
        code += "        api.cache.put(path, data_mat)\n"                
        code += "    else:\n"
        code += "        data_mat = api.cache.get(path)\n"
        code += "    data_mat_list.append(data_mat)\n"
        code += "\n"
        code += "adapter.close()\n"        
        code += "data_mat = np.array(data_mat_list).astype(np.float32)\n"
        code += "data_mat = da.from_array(data_mat)\n"
        code += "%s, %s, %s, %s_size, %s_size, %s_size = split(data_mat, %f, %f, %f)\n" % (var_train, var_valid, var_test,
                                                                                           var_train, var_valid, var_test,
                                                                                           rate_train, rate_valid, rate_test)
        return code


class DataDataCodeGenerator(CodeGenerator):
    def __init__(self, sources, partitions, batch_size, shuffle, seed=0, columns=[], layer_id=None):
        self._seed = seed
        self.batch_size=batch_size
        self.shuffle=shuffle
        self.columns=columns
        self._layer_id = layer_id
        
        self._strategies = []
        self._partitions = []

        # For each source, select strategy. Normalize all partitions.
        for source, partition in zip(sources, partitions):
            if sum(partition) != 100:
                raise ValueError("Partition percentages do not sum to 100!")

            partition = [partition[0]/100.0, partition[1]/100.0, partition[2]/100.0]
            self._partitions.append(partition)
            self._strategies.append(self._select_strategy(source))
        
    def get_code(self):
        code  = 'def split(array, train_rate, test_rate, validation_rate):\n'
        code += '    def generator(array, idx_from, idx_to):\n'
        code += '        for x in array[idx_from:idx_to]:\n'
        #code += '            print("valshapa",x.shape)\n'        
        code += '            yield x.squeeze()\n'
        code += '    \n'
        code += '    array.compute_chunk_sizes()\n'
        code += '    size = len(array)\n'
        code += '    train_size = round(train_rate*size)\n'
        code += '    validation_size = round(validation_rate*size)\n'
        code += '    test_size = size - train_size - validation_size\n'
        code += '    \n'
        code += '    train_gen = generator(array, 0, train_size)\n'
        code += '    validation_gen = generator(array, train_size, train_size+validation_size)        \n'
        code += '    test_gen = generator(array, train_size+validation_size, size)\n'
        code += '    return train_gen, test_gen, validation_gen, train_size, test_size, validation_size\n'
        code += '\n'        
        code += 'np.random.seed(%d)\n' % self._seed
        code += '\n'

        # Get remaining code using strategy
        if len(self._strategies) == 1:
            code += self._get_code_single_strategy()
        elif len(self._strategies) > 1:
            code += self._get_code_multi_strategy()
        else:
            raise ValueError('negative number of strategies??')

        return code
    
    def _get_code_single_strategy(self):
        strategy, partition = self._strategies[0], self._partitions[0]
        code = strategy.execute(var_train='X_train',
                                var_valid='X_validation',
                                var_test='X_test',
                                rate_train=partition[0],
                                rate_valid=partition[1],
                                rate_test=partition[2])
        code += '\n'
        code += '# Tensorflow wants generators wrapped in functions\n'
        code += 'def wrap(gen):\n'
        code += '    def func():\n'
        code += '        return gen\n'
        code += '    return func\n'
        code += '\n'
        code += 'print("TYPE TYPE TYPE TYPE TYPE", X_train)\n'
        code += 'X_train = wrap(X_train)\n'
        code += 'X_validation = wrap(X_validation)\n'
        code += 'X_test = wrap(X_test)\n'                
        code += '\n'        
        code += self._get_code_common()
        return code
    
    def _get_code_multi_strategy(self):
        mask_trn = 'X{}_train'
        mask_tst = 'X{}_test'
        mask_vld = 'X{}_validation'
        
        code = ''
        # Load each dataset and split it
        for counter, (strategy, partition) in enumerate(zip(self._strategies, self._partitions)):
            code += strategy.execute(var_train=mask_trn.format(counter),
                                          var_valid=mask_vld.format(counter),
                                          var_test=mask_tst.format(counter),
                                          rate_train=partition[0],
                                          rate_valid=partition[1],                                          
                                          rate_test=partition[2])
        code += '\n'
        code += 'def chain(*generators):\n'
        code += '    def func():\n'
        code += '        for g in generators:\n'
        code += '            yield from g\n'
        code += '    return func\n'
        code += '\n'
            
        # Concatenation        
        n_sets = len(self._partitions)
        list_str_trn = ", ".join([mask_trn.format(i) for i in range(n_sets)])
        list_str_val = ", ".join([mask_vld.format(i) for i in range(n_sets)])
        list_str_tst = ", ".join([mask_tst.format(i) for i in range(n_sets)])
        code += "X_train = chain(%s)\n" % list_str_trn 
        code += "X_validation = chain(%s)\n" % list_str_val
        code += "X_test = chain(%s)\n" % list_str_tst
        code += '\n'
        list_str_trn = "_size, ".join([mask_trn.format(i) for i in range(n_sets)])+'_size'
        list_str_val = "_size, ".join([mask_vld.format(i) for i in range(n_sets)])+'_size'
        list_str_tst = "_size, ".join([mask_tst.format(i) for i in range(n_sets)])+'_size'
        code += 'X_train_size = sum([%s])\n' % list_str_trn
        code += 'X_validation_size = sum([%s])\n' % list_str_val
        code += 'X_test_size = sum([%s])\n' % list_str_tst
        code += '\n'        
        code += self._get_code_common()
        return code

    def _get_code_common(self):
        code  = '\n'
        code += "global _data_size\n"
        code += "_data_size=np.array([X_train_size, X_validation_size, X_test_size])\n"
        code += "_partition_summary = list(_data_size*100/sum(_data_size))\n"
        code += "_batch_size = %d\n" % int(self.batch_size)
        code += "api.data.store(batch_size=_batch_size)\n"        
        code += "\n"
        code += 'X_train = tf.data.Dataset.from_generator(X_train, output_types=np.float32)\n'
        code += 'X_validation = tf.data.Dataset.from_generator(X_validation, output_types=np.float32)\n'
        code += 'X_test = tf.data.Dataset.from_generator(X_test, output_types=np.float32)\n'        
        code += "\n"
        if self.shuffle:
            code += "X_train=X_train.shuffle(X_train_size,seed=%d).batch(_batch_size)\n" % self._seed
        else:
            code += "X_train=X_train.batch(_batch_size)\n"
        code += "X_validation=X_validation.batch(_batch_size)\n"
        code += "X_test=X_test.batch(1)\n"
        code += "\n"
        code += "iterator = tf.data.Iterator.from_structure(X_train.output_types, X_train.output_shapes)\n"
        code += "train_iterator = iterator.make_initializer(X_train, name='train_iterator_%s')\n" % self._layer_id
        code += "validation_iterator = iterator.make_initializer(X_validation, name='validation_iterator_%s')\n" % self._layer_id        
        code += "test_iterator = iterator.make_initializer(X_test, name='test_iterator_%s')\n" % self._layer_id                
        code += "Y = next_elements = iterator.get_next()\n"
        return code        

    def _select_strategy(self, source):
        if source['type'] == 'file':
            strategy = self._select_file_strategy(file_path=os.path.abspath(source['path']).replace("\\","\\\\"))
        elif source['type'] == 'directory':
            strategy = self._select_directory_strategy(directory_path=os.path.abspath(source['path']).replace("\\","\\\\"))
        elif source['type'] == 's3bucket':
            strategy = self._select_s3bucket_strategy(bucket=source['bucket'],
                                                      region_name=source['region_name'],
                                                      delimiter=source['delimiter'],
                                                      prefix=source['prefix'],
                                                      aws_access_key_id=source['aws_access_key_id'],
                                                      aws_secret_access_key=source['aws_secret_access_key'])
        return strategy
    
    def _select_file_strategy(self, file_path):
        _, ext = os.path.splitext(file_path)

        if ext in ['.npy', '.npz']:
            strategy = FileNumpyStrategy(file_path)
        elif ext in ['.csv', '.txt']:
            strategy = FileCsvStrategy(file_path, self.columns)
        else:
            raise NotImplementedError("Extension {} not implemented".format(ext))
        
        return strategy    

    def _select_directory_strategy(self, directory_path):
        file_paths = os.listdir(directory_path)
        extensions = [os.path.splitext(p)[1] for p in file_paths]
        
        if len(set(extensions)) != 1:
            raise ValueError("Can only contain one (and atleast one) type of file!")        

        ext = extensions[0]
        if ext in ['.jpg', '.png', '.jpeg', '.tif', '.tiff']:
            strategy = DirectoryImageStrategy(directory_path)
        else:
            raise NotImplementedError("Extension {} not implemented".format(ext))            
            
        return strategy

    def _select_s3bucket_strategy(self, bucket, region_name, delimiter, prefix,
                                  aws_access_key_id, aws_secret_access_key):
        adapter = S3BucketAdapter(bucket, region_name, aws_access_key_id, aws_secret_access_key)
        file_keys = adapter.get_keys(delimiter, prefix)
        extensions = [os.path.splitext(p)[1] for p in file_keys]        
        
        if len(set(extensions)) != 1:
            raise ValueError("Can only contain one (and atleast one) type of file!")        
        
        ext = extensions[0]
        if ext in ['.jpg', '.png', '.jpeg', '.tiff', '.tif']:
            strategy = S3BucketImageStrategy(bucket, region_name, delimiter, prefix,
                                             aws_access_key_id, aws_secret_access_key)
        elif ext in ['.json']:
            strategy = S3BucketJsonStrategy(bucket, region_name, delimiter, prefix,
                                            aws_access_key_id, aws_secret_access_key)
        else:
            raise NotImplementedError("Extension {} not implemented".format(ext))

        return strategy

if __name__ == "__main__":
    def runrunrun(sources, partitions):
        cg = DataDataCodeGenerator(sources, partitions)
        code = cg.get_code()
        
        import tensorflow as tf
        import numpy as np
        import os
        import skimage
        import json
        import pandas as pd        
        
        globals_ = {'tf': tf,
                    'os': os, #TODO: FARLIGT ATT GE ACCESS TILL OS?
                    'skimage': skimage,
                    'pd': pd,
                    'json': json,
                    'S3BucketAdapter': S3BucketAdapter,                    
                    'np': np}        
        locals_ = {}
        
        print("Executing code:")
        print("------------------")
        print(code)
        print("------------------")
        exec(code, globals_, locals_)

        print("Local variables: ", locals_)
        
        import pdb; pdb.set_trace()

        
    
    # List of files
    sources = [{'type': 'file', 'path': 'mnist_split/mnist_input.npy'},
               {'type': 'file', 'path': 'mnist_split/mnist_input.npy'}]

    partitions = [(70, 20, 10), (70, 20, 10)]

    runrunrun(sources, partitions)
    

    
    # Image directory    
    sources = [{'type': 'directory', 'path': 'rand_imgs/'}]
    partitions = [(70, 20, 10)]

    runrunrun(sources, partitions)

    
    # S3 bucket
    sources = [{'type': 's3bucket',
                'bucket': 'perceptitest',
                'region_name': 'eu-north-1',
                'delimiter': '',
                'prefix': '',
                'aws_access_key_id': "AKIAZYLA7ETUIOS73NHX",
                'aws_secret_access_key': "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"}]

    partitions = [(70, 20, 10)]
    
    runrunrun(sources, partitions)

