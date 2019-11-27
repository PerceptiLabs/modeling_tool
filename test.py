import numpy as np
import dask.dataframe as dd
import dask.array as da
import tensorflow as tf
from unittest.mock import MagicMock

api = MagicMock()

np.random.seed(0)

if 'C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\Verizon\\anomhoststraining.csv' not in api.cache:
    df = dd.read_csv('C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\Verizon\\anomhoststraining.csv', blocksize='100MB')
    api.cache.put('C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\Verizon\\anomhoststraining.csv', df)
else:
    df = api.cache.get('C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\Verizon\\anomhoststraining.csv')
cols = list(df.columns)
# df = df[['hostname']]
global df_train, df_validation, df_test
df_train, df_validation, df_test = df.random_split([0.700000, 0.200000, 0.100000], random_state=0)

types = tuple(t if t is not np.dtype('O') else tf.string for t in tuple(df.dtypes))


def X_train():
    global df_train
    def generator(df):
         for x in df.iterrows():
             y = x[1].values.squeeze()
             yield y
    return generator(df_train)
def X_validation():
    global df_validation
    def generator(df):
         for x in df.iterrows():
             y = x[1].values.squeeze()
             yield y
    return generator(df_validation)
def X_test():
    global df_test
    def generator(df):
         for x in df.iterrows():
             y = x[1].values.squeeze()
             yield y
    return generator(df_test)

# The size estimates are only used for visualizations
if 'C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\Verizon\\anomhoststraining.csv_size' not in api.cache:
    size = len(df.partitions[0])*df.npartitions
    api.cache.put('C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\Verizon\\anomhoststraining.csv_size', size)
else:
    size = api.cache.get('C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\Verizon\\anomhoststraining.csv_size')
X_train_size = round(0.700000*size)
X_validation_size = round(0.200000*size)
X_test_size = size - X_train_size - X_validation_size

# Tensorflow wants generators wrapped in functions


global _data_size
_data_size=np.array([X_train_size, X_validation_size, X_test_size])
_partition_summary = list(_data_size*100/sum(_data_size))
_batch_size = 10
api.data.store(batch_size=_batch_size)
# import pdb; pdb.set_trace()
X_train = tf.data.Dataset.from_generator(X_train, output_types=types)
X_validation = tf.data.Dataset.from_generator(X_validation, output_types=types)
X_test = tf.data.Dataset.from_generator(X_test, output_types=types)

X_train=X_train.batch(_batch_size)
X_validation=X_validation.batch(_batch_size)
X_test=X_test.batch(1)

iterator = tf.data.Iterator.from_structure(X_train.output_types, X_train.output_shapes)
train_iterator = iterator.make_initializer(X_train, name='train_iterator_1564399775664')
validation_iterator = iterator.make_initializer(X_validation, name='validation_iterator_1564399775664')
test_iterator = iterator.make_initializer(X_test, name='test_iterator_1564399775664')
# import pdb; pdb.set_trace()
Y = next_elements = iterator.get_next()
sess=tf.Session()
sess.run(train_iterator)
sess.run(Y)
import pdb; pdb.set_trace()

# import tensorflow as tf
# import dask.dataframe as dd
# import numpy as np
# import pandas as pd
# a = np.array(['a', 'b', 'c'], dtype=object)
# b = np.array([1, 2, 3], dtype=np.int32)
# c = np.array([1.0, 2.0, 3.0], dtype=np.float32)
# df = pd.DataFrame({'a': a, 'b': b, 'c': c})
# df = dd.from_pandas(df, npartitions=1)
# def make_gen():
#     def gen():
#         for row in df.iterrows():
#             x = tuple(row[1].values.squeeze())
#             yield x
#     return gen()
# X = tf.data.Dataset.from_generator(make_gen, output_types=tuple(df.dtypes))
# nxt = X.make_one_shot_iterator().get_next()
# sess = tf.Session()
# for i in range(10):
#     x = sess.run(nxt)
#     print(x)
#     import pdb;pdb.set_trace()
