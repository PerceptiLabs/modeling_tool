import pytest
import ast

from code_generator.tensorflow import *


class TestConvCode:
    def test_syntax_1D(self):
        gen = ConvCodeGenerator('1D', 1, 2, 3, 'SAME')
        code = gen.get_code()
        ast.parse(code) # Can raise SyntaxError => test fails.

    def test_runs_1D(self):
        gen = ConvCodeGenerator('1D', 1, 2, 3, 'SAME')
        code = gen.get_code()

        import tensorflow as tf
        import numpy as np
        
        tf.enable_eager_execution()
        X = np.zeros((2, 10, 7)) # batch_size, n_samples, n_dims
        X = tf.constant(X, dtype=tf.float32, name='X')
        
        locals_ = {'X': X}
        exec(code, {'tf': tf, 'np': np}, locals_)
        Y = locals_['Y']

        assert np.all(Y.numpy() == 0.1) # 0.1 is the default bias :)

    def test_syntax_2D(self):
        gen = ConvCodeGenerator('2D', 1, 2, 3, 'SAME')
        code = gen.get_code()
        ast.parse(code)
        
    def test_runs_2D(self):
        gen = ConvCodeGenerator('2D', 1, 2, 3, 'SAME')
        code = gen.get_code()

        import tensorflow as tf
        import numpy as np
        
        tf.enable_eager_execution()
        X = np.zeros((2, 10, 7, 7)) # batch_size, n_samples, n_dims, n_dims
        X = tf.constant(X, dtype=tf.float32, name='X')
        
        locals_ = {'X': X}
        exec(code, {'tf': tf, 'np': np}, locals_)
        Y = locals_['Y']

        assert np.all(Y.numpy() == 0.1)
        
    def test_syntax_3D(self):
        gen = ConvCodeGenerator('3D', 1, 2, 3, 'SAME')
        code = gen.get_code()
        ast.parse(code)
        
    def test_runs_3D(self):
        gen = ConvCodeGenerator('3D', 1, 2, 3, 'SAME')
        code = gen.get_code()

        import tensorflow as tf
        import numpy as np
        
        tf.enable_eager_execution()
        X = np.zeros((2, 10, 7, 7, 7)) # batch_size, n_samples, n_dims, n_dims, n_dims
        X = tf.constant(X, dtype=tf.float32, name='X')
        
        locals_ = {'X': X}
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
        gen = FullyConnectedCodeGenerator(10, 'Sigmoid')
        code = gen.get_code()
        ast.parse(code)
    
    
