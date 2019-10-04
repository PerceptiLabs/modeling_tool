import pytest
from unittest import mock
import ast
import numpy as np
import tensorflow as tf
from tensorflow.python.eager.context import context, EAGER_MODE, GRAPH_MODE
        
from code_generator.tensorflow import *


def switch_to(mode):
    #Hack to turn eager mode on and off so it does not affect the computational core (since eager mode is global) (can be a problem if running when core already is started?)
    ctx = context()._eager_context
    ctx.mode = mode
    ctx.is_eager = mode == EAGER_MODE

class TestConvCode:
    def test_syntax_1D(self):
        gen = ConvCodeGenerator(0, '1D', 1, 2, 3, "'SAME'")
        code = gen.get_code()
        ast.parse(code) # Can raise SyntaxError => test fails.

    def test_runs_1D(self):
        gen = ConvCodeGenerator(0, '1D', 1, 2, 3, "'SAME'")
        code = gen.get_code()

        switch_to(EAGER_MODE)
        X = np.zeros((2, 10, 7)) # batch_size, n_samples, n_dims
        X = tf.constant(X, dtype=tf.float32, name='X')
        
        locals_ = {'X': {'Y': X}}                
        exec(code, {'tf': tf, 'np': np}, locals_)
        Y = locals_['Y']

        assert np.all(Y.numpy() == 0.1) # 0.1 is the default bias :)

    def test_syntax_2D(self):
        gen = ConvCodeGenerator(0, '2D', 1, 2, 3, "'SAME'")
        code = gen.get_code()
        ast.parse(code)
        
    def test_runs_2D(self):
        gen = ConvCodeGenerator(0, '2D', 1, 2, 3, "'SAME'")
        code = gen.get_code()

        switch_to(EAGER_MODE)        
        X = np.zeros((2, 10, 7, 7)) # batch_size, n_samples, n_dims, n_dims
        X = tf.constant(X, dtype=tf.float32, name='X')
        
        locals_ = {'X': {'Y': X}}
        exec(code, {'tf': tf, 'np': np}, locals_)
        Y = locals_['Y']

        assert np.all(Y.numpy() == 0.1)
        
    def test_syntax_3D(self):
        gen = ConvCodeGenerator(0, '3D', 1, 2, 3, "'SAME'")
        code = gen.get_code()
        ast.parse(code)
        
    def test_runs_3D(self):
        gen = ConvCodeGenerator(0, '3D', 1, 2, 3, "'SAME'")
        code = gen.get_code()

        switch_to(EAGER_MODE)                
        X = np.zeros((2, 10, 7, 7, 7)) # batch_size, n_samples, n_dims, n_dims, n_dims
        X = tf.constant(X, dtype=tf.float32, name='X')
        
        locals_ = {'X': {'Y': X}}        
        exec(code, {'tf': tf, 'np': np}, locals_)
        Y = locals_['Y']

        assert np.all(Y.numpy() == 0.1)

        
class TestReshape:
    def test_syntax(self):
        gen = ReshapeCodeGenerator([28, 28, 1], [0, 1, 2])
        code = gen.get_code()
        ast.parse(code)

        
class TestRecurrent:
    def test_syntax_lstm(self):
        gen = RecurrentCodeGenerator('LSTM', 2, 10, False)
        code = gen.get_code()
        ast.parse(code)
        
    def test_syntax_rnn(self):
        gen = RecurrentCodeGenerator('RNN', 2, 10, False)
        code = gen.get_code()
        ast.parse(code)
        
    def test_syntax_gru(self):
        gen = RecurrentCodeGenerator('GRU', 2, 10, False)
        code = gen.get_code()
        ast.parse(code)
        

class TestWordEmbedding:
    def test_syntax(self):
        gen = WordEmbeddingCodeGenerator()
        code = gen.get_code()
        ast.parse(code)

        
class TestOneHot:
    def test_syntax(self):
        gen = OneHotCodeGenerator(10)
        code = gen.get_code()
        ast.parse(code)


class TestCrop:
    def test_syntax(self):
        gen = CropCodeGenerator(3, 4, 5, 6)
        code = gen.get_code()
        ast.parse(code)

        
class TestGrayscale:
    def test_syntax(self):
        gen = GrayscaleCodeGenerator()
        code = gen.get_code()
        ast.parse(code)

        
class TestArgmax:
    def test_syntax(self):
        gen = ArgmaxCodeGenerator(1)
        code = gen.get_code()
        ast.parse(code)


class TestSoftmax:
    def test_syntax(self):
        gen = SoftmaxCodeGenerator()
        code = gen.get_code()
        ast.parse(code)

        
class TestMerge:
    def test_syntax_concat(self):
        gen = MergeCodeGenerator('Concat', 0)
        code = gen.get_code()
        ast.parse(code)
        
    def test_syntax_add(self):
        gen = MergeCodeGenerator('Add', 0)
        code = gen.get_code()
        ast.parse(code)
        
    def test_syntax_subtract(self):
        gen = MergeCodeGenerator('Sub', 0)
        code = gen.get_code()
        ast.parse(code)
        
    def test_syntax_multiply(self):
        gen = MergeCodeGenerator('Multi', 0)
        code = gen.get_code()
        ast.parse(code)
        
    def test_syntax_divide(self):
        gen = MergeCodeGenerator('Div', 0)
        code = gen.get_code()
        ast.parse(code)
    
    
class TestFullyConnected:
    def test_syntax(self):
        gen = FullyConnectedCodeGenerator(0, 10, 'Sigmoid')
        code = gen.get_code()
        ast.parse(code)
    
    
class TestTrainNormal:
    def test_syntax(self):
        network_branch = TrainInputBranch(direct_layer='1564399782856', data_layer='1564399775664')
        labels_branch = TrainInputBranch(direct_layer='1564399782856', data_layer='1564399786876')
        gen = TrainNormalCodeGenerator(network_branch, labels_branch, n_epochs=2, n_iterations=3)
        code = gen.get_code()
        ast.parse(code)

    def test_training_converges(self):
        switch_to(GRAPH_MODE)
        np.random.seed(0)
        tf.set_random_seed(0)

        # Set up input branch to the data layers
        network_branch = TrainInputBranch(direct_layer='1564399782856', data_layer='1564399775664')
        labels_branch = TrainInputBranch(direct_layer='1564399788744', data_layer='1564399786876')

        
        # Setup X
        X_ = np.array([[1, 2, 3],
                       [7, 8, 9]], dtype=np.float32)
        X_train = tf.data.Dataset.from_tensor_slices(X_).repeat().batch(2)
        iterator = tf.data.Iterator.from_structure(X_train.output_types, X_train.output_shapes)
        X_init = iterator.make_initializer(X_train,
                                           name='train_iterator_{}'.format(network_branch.data_layer))
        X = iterator.get_next()

        # Setup Y
        y_ = np.array([[0], [1]], dtype=np.float32)
        y_train = tf.data.Dataset.from_tensor_slices(y_).repeat().batch(2)
        iterator = tf.data.Iterator.from_structure(y_train.output_types, y_train.output_shapes)
        y_init = iterator.make_initializer(y_train,
                                           name='train_iterator_{}'.format(labels_branch.data_layer))
        y = iterator.get_next()

        # Setup a network
        W1 = tf.Variable(tf.truncated_normal(shape=[3,10], stddev=0.01))
        b1 = tf.Variable(tf.constant(0.01))
        z1 = tf.matmul(X, W1) + b1
        #z1 = tf.nn.relu(z1)
        
        W2 = tf.Variable(tf.truncated_normal(shape=[10,1], stddev=0.01))
        b2 = tf.Variable(tf.constant(0.01))
        z2 = tf.matmul(z1, W2) + b2
        #z2 = tf.sigmoid(z1)        


        # Set up training code generator
        gen = TrainNormalCodeGenerator(network_branch, labels_branch,
                                       n_epochs=5, n_iterations=1000)
        training_code = gen.get_code_parts()[0].code

        # Set up locals
        X = {
            network_branch.direct_layer: {'Y': z2},
            labels_branch.direct_layer: {'Y': y}
        }

        api = mock.Mock()
        api.control.epoch_loop = lambda x: range(x)
        api.control.training_iteration_loop = lambda x: range(x)
        api.control.validation_iteration_loop = lambda x: range(x)
        api.control.testing_iteration_loop = lambda x: range(x)                        
        locals_ = {'X': X, 'api': api}

        # Run code
        exec(training_code, {'tf': tf, 'np': np}, locals_)


        # Check that output has converged!
        sess = locals_['sess']
        sess.run(X_init) # Reset the dataset
        sess.run(y_init)

        y_pred = locals_['y_pred']
        y_pred_ = sess.run(y_pred)

        assert np.all(np.isclose(y_pred_, y_).squeeze())
