import numpy as np
import dask.dataframe as dd
import dask.array as da
import tensorflow as tf
from unittest.mock import MagicMock

tf.enable_eager_execution()

api = MagicMock()

# np.random.seed(0)

# if 'C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\Verizon\\anomhoststraining.csv' not in api.cache:
#     df = dd.read_csv('C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\Verizon\\anomhoststraining.csv', blocksize='100MB')
#     api.cache.put('C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\Verizon\\anomhoststraining.csv', df)
# else:
#     df = api.cache.get('C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\Verizon\\anomhoststraining.csv')
# cols = list(df.columns)
# df = df[[cols[0], cols[2], cols[3]]]
# global df_train, df_validation, df_test
# df_train, df_validation, df_test = df.random_split([0.700000, 0.200000, 0.100000], random_state=0)

# types = tuple(t if t is not np.dtype('O') else tf.string for t in tuple(df.dtypes))


# def X_train():
#     global df_train
#     def generator(df):
#          for x in df.iterrows():
#              y = x[1].values.squeeze()
#              yield y
#     return generator(df_train)
# def X_validation():
#     global df_validation
#     def generator(df):
#          for x in df.iterrows():
#              y = x[1].values.squeeze()
#              yield y
#     return generator(df_validation)
# def X_test():
#     global df_test
#     def generator(df):
#          for x in df.iterrows():
#              y = x[1].values.squeeze()
#              yield y
#     return generator(df_test)

# # The size estimates are only used for visualizations
# if 'C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\Verizon\\anomhoststraining.csv_size' not in api.cache:
#     size = len(df.partitions[0])*df.npartitions
#     api.cache.put('C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\Verizon\\anomhoststraining.csv_size', size)
# else:
#     size = api.cache.get('C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\Verizon\\anomhoststraining.csv_size')
# X_train_size = round(0.700000*size)
# X_validation_size = round(0.200000*size)
# X_test_size = size - X_train_size - X_validation_size
# _data_shape=next(X_train())
# # Tensorflow wants generators wrapped in functions


# global _data_size
# _data_size=np.array([X_train_size, X_validation_size, X_test_size])
# _partition_summary = list(_data_size*100/sum(_data_size))
# _batch_size = 10
# api.data.store(batch_size=_batch_size)

# import pdb; pdb.set_trace()

# X_train = tf.data.Dataset.from_generator(X_train, output_shapes=_data_shape, output_types=tf.float32)
# X_validation = tf.data.Dataset.from_generator(X_validation, output_shapes=_data_shape, output_types=tf.float32)
# X_test = tf.data.Dataset.from_generator(X_test, output_shapes=_data_shape, output_types=tf.float32)

# X_train=X_train.batch(_batch_size)
# X_validation=X_validation.batch(_batch_size)
# X_test=X_test.batch(1)

# iterator = tf.data.Iterator.from_structure(X_train.output_types, X_train.output_shapes)
# train_iterator = iterator.make_initializer(X_train, name='train_iterator_1564399775664')
# validation_iterator = iterator.make_initializer(X_validation, name='validation_iterator_1564399775664')
# test_iterator = iterator.make_initializer(X_test, name='test_iterator_1564399775664')
# # import pdb; pdb.set_trace()
# Y = next_elements = iterator.get_next()
# sess=tf.Session()
# sess.run(train_iterator)
# sess.run(Y)
# import pdb; pdb.set_trace()







def split(array__, train_rate, test_rate, validation_rate):
    def generator(array_, idx_from, idx_to):
        for x in array_[idx_from:idx_to]:
            yield x.squeeze().astype(np.float32)
    
    global array, train_size, validation_size, size
    array=array__
    array.compute_chunk_sizes()
    size = len(array)
    train_size = round(train_rate*size)
    validation_size = round(validation_rate*size)
    test_size = size - train_size - validation_size
    
    def train_gen():
        global array, train_size
        def generator(array_, idx_from, idx_to):
            for x in array_[idx_from:idx_to]:
                yield x.squeeze().astype(np.float32)
        return generator(array, 0, train_size)
    def validation_gen():
        global array, train_size, validation_size
        def generator(array_, idx_from, idx_to):
            for x in array_[idx_from:idx_to]:
                yield x.squeeze().astype(np.float32)
        return generator(array, train_size, train_size+validation_size)
    def test_gen():
        global array, train_size, validation_size, size
        def generator(array_, idx_from, idx_to):
            for x in array_[idx_from:idx_to]:
                yield x.squeeze().astype(np.float32)
        return generator(array, train_size+validation_size, size)
    return train_gen, validation_gen, test_gen, train_size, validation_size, test_size

np.random.seed(0)

if 'C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\mnist_split\\mnist_input.npy' not in api.cache:
    data_mat = np.load('C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\mnist_split\\mnist_input.npy').astype(np.float32)
    api.cache.put('C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\mnist_split\\mnist_input.npy', data_mat)
else:
    data_mat = api.cache.get('C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\mnist_split\\mnist_input.npy')
data_mat = da.from_array(data_mat)
types=tf.float32
X_train, X_validation, X_test, X_train_size, X_validation_size, X_test_size = split(data_mat, 0.700000, 0.200000, 0.100000)

# Tensorflow wants generators wrapped in functions


global _data_size
_data_shape = np.shape(next(X_train()))
_data_size=np.array([X_train_size, X_validation_size, X_test_size])
_partition_summary = list(_data_size*100/sum(_data_size))
_batch_size = 10
api.data.store(batch_size=_batch_size)
import pdb; pdb.set_trace()
X_train = tf.data.Dataset.from_generator(X_train, output_shapes=_data_shape, output_types=np.float32)
X_validation = tf.data.Dataset.from_generator(X_validation, output_shapes=_data_shape, output_types=np.float32)
X_test = tf.data.Dataset.from_generator(X_test, output_shapes=_data_shape, output_types=np.float32)

X_train=X_train.batch(_batch_size)
X_validation=X_validation.batch(_batch_size)
X_test=X_test.batch(1)

iterator = tf.data.Iterator.from_structure(X_train.output_types, X_train.output_shapes)
train_iterator = iterator.make_initializer(X_train, name='train_iterator_1574941595917')
validation_iterator = iterator.make_initializer(X_validation, name='validation_iterator_1574941595917')
test_iterator = iterator.make_initializer(X_test, name='test_iterator_1574941595917')
Y = next_elements = iterator.get_next()
