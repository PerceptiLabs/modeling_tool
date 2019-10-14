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
        # code += "np.random.shuffle(data_mat)\n"
        code += "%s, %s, %s = split(data_mat, %f, %f, %f)\n" % (var_train, var_valid, var_test,
                                                                rate_train, rate_valid, rate_test)
        return code

    
class FileCsvStrategy(AbstractStrategy):
    def __init__(self, path, columns):
        self._path = path
        self._columns=columns
        
    def execute(self, var_train, var_valid, var_test, rate_train, rate_valid, rate_test):
        code  = "if '%s' not in api.cache:\n" % self._path        
        code += "    df = pd.read_csv('%s')\n" % self._path
        code += "    cols = list(df.columns)\n"
        if self._columns:
            code += "    data_mat = df[%s].to_numpy().astype(np.float32)\n" % str(["cols[%d]" % i for i in self._columns]).replace("'","")
        else:
            code += "    data_mat = df.to_numpy().astype(np.float32)\n"
        code += "    api.cache.put('%s', data_mat)\n" % self._path            
        code += "else:\n"
        code += "    data_mat = api.cache.get('%s')\n" % self._path        
        code += "%s, %s, %s = split(data_mat, %f, %f, %f)\n" % (var_train, var_valid, var_test,
                                                                rate_train, rate_valid, rate_test)
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
        code += "%s, %s, %s = split(data_mat, %f, %f, %f)\n" % (var_train, var_valid, var_test,
                                                                rate_train, rate_valid, rate_test)
        return code

        
class S3BucketImageStrategy(AbstractStrategy):
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
        code += "%s, %s, %s = split(data_mat, %f, %f, %f)\n" % (var_train, var_valid, var_test,
                                                                rate_train, rate_valid, rate_test)
        return code

    
class S3BucketJsonStrategy(AbstractStrategy):
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
        code += "%s, %s, %s = split(data_mat, %f, %f, %f)\n" % (var_train, var_valid, var_test,
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
        
    def get_code(self, mode='normal'):
        code = ''
        code += 'np.random.seed(%d)\n\n' % self._seed
        
        # Split dataset function [TODO: optional if 100% in train set?]
        code += 'def split(dataset, train_rate, test_rate, validation_rate):\n'
        code += '    size = len(dataset)\n'
        code += '    i1 = round(train_rate*size)\n'
        code += '    i2 = i1 + round(test_rate*size)\n'
        code += '    \n'
        code += '    train = dataset[0:i1]\n'
        code += '    validation = dataset[i1:i2]\n'
        code += '    test = dataset[i2:]\n'
        code += '    return train, validation, test\n'
        code += '\n'

        # Get remaining code using strategy
        if len(self._strategies) == 1:
            code += self._get_code_single_strategy()
        elif len(self._strategies) > 1:
            code += self._get_code_multi_strategy()
        else:
            raise ValueError

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
            
        # Concatenation        
        n_sets = len(self._partitions)
        list_str_trn = ", ".join([mask_trn.format(i) for i in range(n_sets)])
        list_str_val = ", ".join([mask_vld.format(i) for i in range(n_sets)])
        list_str_tst = ", ".join([mask_tst.format(i) for i in range(n_sets)])
        code += "X_train = np.vstack([%s])\n" % list_str_trn
        code += "X_validation = np.vstack([%s])\n" % list_str_val
        code += "X_test = np.vstack([%s])\n" % list_str_tst
        code += '\n'
        code += self._get_code_common()
        return code

    def _get_code_common(self):
        code  = "# Shapes, preview and batch sizes\n"
        code += 'X_train_size = X_train.shape[0]\n'
        code += "X_validation_size = X_validation.shape[0]\n"
        code += "X_test_size = X_test.shape[0]\n"
        code += '\n'
        code += "_sample = X_train[0]\n"
        code += "_data_size=np.array([X_train_size, X_validation_size, X_test_size])\n"
        code += "_partition_summary = list(_data_size*100/sum(_data_size))\n"
        code += "_batch_size = %d\n" % int(self.batch_size)
        code += "api.data.store(sample=_sample)\n"        
        code += "api.data.store(batch_size=_batch_size)\n"        
        code += "\n"
        code += 'X_train = tf.data.Dataset.from_tensor_slices(X_train)\n'
        code += 'X_validation = tf.data.Dataset.from_tensor_slices(X_validation)\n'
        code += 'X_test = tf.data.Dataset.from_tensor_slices(X_test)\n'
        code += "\n"
        
        # if self.shuffle:
        #     code += "X_train=X_train.shuffle(X_train_size,seed=%d).repeat().batch(_batch_size)\n" % self._seed
        # else:
        #     code += "X_train=X_train.repeat().batch(_batch_size)\n"
        # code += "X_validation=X_validation.repeat().batch(_batch_size)\n"
        # code += "X_test=X_test.repeat(1).batch(1)\n"
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

        if ext == '.npy':
            strategy = FileNumpyStrategy(file_path)
        elif ext == '.csv':
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
        if ext in ['.jpg', '.png']:
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
        if ext in ['.jpg', '.png']:
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

