from collections import namedtuple

from code_generator import CodeGenerator, CodePart


def get_activation_code(var_in, var_out, func=None):
    if func is None:
        code = '%s = %s\n' % (var_out, var_in)
    else:
        if func == 'Sigmoid':
            func = 'tf.sigmoid'
        elif func == 'ReLU':
            func = 'tf.nn.relu'
        elif func == 'Tanh':
            func = 'tf.tanh'
        else:
            raise ValueError("Unknown activation function '{}'".format(func))
        
        code = '%s = %s(%s)\n' % (var_out, func, var_in)        
    return code


class ReshapeCodeGenerator(CodeGenerator):
    def __init__(self, shape, permutation):
        self._shape = shape
        self._permutation = permutation
        
    def get_code(self, mode='normal'):
        shape_text = ', '.join([str(i) for i in self._shape])
        perm_text = ', '.join([str(i) for i in self._permutation])
        code = ""
        code += "Y=tf.reshape(X['Y'], [-1]+[layer_output for layer_output in [%s]])\n" % shape_text
        code += "Y=tf.transpose(Y,perm=[0]+[i+1 for i in [%s]])\n" % perm_text
        return code

    
class RecurrentCodeGenerator(CodeGenerator):
    def __init__(self, version, time_steps, neurons, return_sequences=False):
        self._version = version
        self._time_steps = time_steps
        self._neurons = neurons
        self._return_sequences = return_sequences

    def get_code(self, mode='normal'):
        code = ''
        if self._version == 'LSTM':
            code += "cell = tf.nn.rnn_cell.LSTMCell(%s, state_is_tuple=True)\n" % self._neurons
        elif self._version == 'GRU':
            code += "cell = tf.nn.rnn_cell.GRUCell(%s, state_is_tuple=True)\n" % self._neurons
        elif self._version == 'RNN':
            code += "cell = tf.nn.rnn_cell.BasicRNNCell(%s, state_is_tuple=True)\n" % self._neurons
            
        code += "node = X['Y']\n"
        code += "rnn_outputs, final_state = tf.nn.dynamic_rnn(cell, node, dtype=node.dtype)\n"
        
        if self._return_sequences:
            code += "Y = rnn_outputs\n"
        else:
            code += "Y = rnn_outputs[:, -1]\n"
            
        return code
    

class WordEmbeddingCodeGenerator(CodeGenerator):
    def get_code(self, mode='normal'):
        code  = 'words = tf.string_split(X)\n'
        code += 'vocab_size=words.get_shape().as_list()[0]\n'
        code += 'embed_size=10\n'
        code += 'embedding = tf.Variable(tf.random_uniform((vocab_size, embed_size), -1, 1))\n'
        code += 'Y = tf.nn.embedding_lookup(embedding, X)\n'
        return code


class OneHotCodeGenerator(CodeGenerator):
    def __init__(self, n_classes):
        self._n_classes = n_classes
        
    def get_code(self, mode='normal'):
        code = "Y=tf.one_hot(tf.cast(X['Y'],dtype=tf.int32), %s)\n" % self._n_classes
        return code

    
class CropCodeGenerator(CodeGenerator):
    def __init__(self, offset_height, offset_width, target_height, target_width):
        self._offset_height = offset_height
        self._offset_width = offset_width
        self._target_height = target_height        
        self._target_width = target_width

    def get_code(self, mode='normal'):
        code = "Y=tf.image.crop_to_bounding_box(X, %d, %d, %d, %d)\n" % (self._offset_height,
                                                                         self._offset_width,
                                                                         self._target_height,
                                                                         self._target_width)
        return code
    

class GrayscaleCodeGenerator(CodeGenerator):
    def get_code(self, mode='normal'):
        code  = 'if X["Y"].get_shape().as_list()[-1] == 3:\n'
        code += '    Y = tf.image.rgb_to_grayscale(X)\n'
        code += 'else:\n'
        code += '    Y = X\n'
        return code


class ArgmaxCodeGenerator(CodeGenerator):
    def __init__(self, dim):
        self._dim = dim

    def get_code(self, mode='normal'):
        code = 'Y = tf.argmax(X, %s)' % self._dim
        return code


class SoftmaxCodeGenerator(CodeGenerator):
    def get_code(self, mode='normal'):
        code = 'Y = tf.nn.softmax(X)'
        return code


class MergeCodeGenerator(CodeGenerator):
    def __init__(self, type_, merge_dim):
        self._type = type_
        self._merge_dim = merge_dim

    def get_code(self, mode='normal'):
        # TODO: in python version < 3.6 dicts aren't ordered. caution if we allow custom environments in the future.
        
        if self._type == 'Concat':
            # Due to duplicate values in X, just take every other value.            
            code  = "for i in range(0, len(list(X['Y'].values())), 2):\n"
            code += "    if not Y:\n"
            code += "        Y = list(X['Y'].values())[i]\n"
            code += "    Y = tf.concat([Y, list(X['Y'].values())[i]], %s)\n" % self._merge_dim
            return code
        elif self._type == 'Add':
            code  = "for i in range(0, len(list(X['Y'].values())), 2):\n"
            code += "    if not Y:\n"
            code += "        Y = list(X['Y'].values())[i]\n"
            code += "    Y = tf.add(list(X['Y'].values())[i], Y)\n"
            return code
        elif self._type == 'Sub':
            code  = "for i in range(0, len(list(X['Y'].values())), 2):\n"
            code += "    if not Y:\n"
            code += "        Y = list(X['Y'].values())[i]\n"
            code += "    Y = tf.subtract(list(X['Y'].values())[i], Y)\n"
            return code            
        elif self._type == 'Multi':
            code  = "for i in range(0, len(list(X['Y'].values())), 2):\n"
            code += "    if not Y:\n"
            code += "        Y = list(X['Y'].values())[i]\n"
            code += "    Y = tf.multiply(list(X['Y'].values())[i], Y)\n"
            return code            
        elif self._type == 'Div':
            code  = "for i in range(0, len(list(X['Y'].values())), 2):\n"
            code += "    if not Y:\n"
            code += "        Y = list(X['Y'].values())[i]\n"
            code += "    Y = tf.divide(list(X['Y'].values())[i], Y)\n"
            return code

class FullyConnectedCodeGenerator(CodeGenerator):
    def __init__(self, layer_id, n_neurons, activation=None, dropout=False, keep_prob=1.0):
        self._layer_id = layer_id
        self._n_neurons = n_neurons
        self._dropout = dropout
        self._keep_prob = keep_prob
        self._activation = activation

    def get_code(self, mode='normal'):
        code  = "input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]\n"
        code += "shape = [input_size, %s]\n" % self._n_neurons
        code += "initial = tf.truncated_normal(shape, stddev=0.1)\n"
        code += "W = tf.Variable(initial, name='weights-%s')\n" % self._layer_id
        code += "initial = tf.constant(0.1, shape=[%s])\n" % self._n_neurons
        code += "b = tf.Variable(initial, name='bias-%s')\n" % self._layer_id
        code += "flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)\n"
        code += "node = tf.matmul(flat_node, W)\n"

        if self._dropout:
            code += "node=tf.nn.dropout(node, %f)\n" % self._keep_prob

        code += "node = node + b\n"
        code += "\n"
        code += get_activation_code(var_out='Y', var_in='node', func=self._activation)
        return code

    
class ConvCodeGenerator(CodeGenerator):
    def __init__(self, layer_id, conv_dim, patch_size, feature_maps, stride, padding,
                 dropout=False, keep_prob=None, activation=None,
                 pool=False, pooling=None, pool_area=None, pool_padding=None, pool_stride=None):
        self._layer_id = layer_id
        self._conv_dim = conv_dim
        self._patch_size = patch_size
        self._feature_maps = feature_maps
        self._stride = stride
        self._padding = padding
        self._dropout = dropout
        self._keep_prob = keep_prob
        self._activation = activation
        self._pool = pool
        self._pooling = pooling
        self._pool_area = pool_area
        self._pool_padding = pool_padding
        self._pool_stride = pool_stride

    def get_code(self, mode='normal'):
        code = ''
        
        # Get the main code
        if self._conv_dim == "1D":
            code += self._get_code_1d()
        elif self._conv_dim == "2D":
            code += self._get_code_2d()            
        elif self._conv_dim == "3D":
            code += self._get_code_3d()
        elif self._conv_dim == "Automatic":
            code += self._get_code_autodim()

        if self._dropout:
            code += "tf.nn.dropout(node, %f)\n\n" % self._keep_prob

        # Activation
        code += "node = node + b\n"
        code += get_activation_code(var_out='Y', var_in='node', func=self._activation)
            
        # Pooling        
        if self._pool and self._pooling == "Max":
            if self._conv_dim != "Automatic":
                code += "dim_str = '%s'\n" % self._conv_dim
            else:
                code += "dim_str = str(len(X['Y'].get_shape().as_list())-1)+'D'\n"

            code += "Y = tf.nn.max_pool(Y, %s, %s, '%s', dim_str)" % (self._pool_area, self._pool_stride, self._pool_padding)
        if self._pool and self._pooling == "Mean":
            code += "Y = tf.nn.pool(Y, window_shape=%s, pooling_type='AVG', padding=%s, strides=%s)" % (self._pool_area, self._pool_padding, self._pool_stride)            
        return code

    def _get_code_1d(self):
        code  = "shape = [%s, X['Y'].get_shape().as_list()[-1], %s]\n" % (self._patch_size, self._feature_maps)
        code += "initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(%s**2 + %s)))\n" % (self._patch_size, self._feature_maps)
        code += "W = tf.Variable(initial, name='weights-%s')\n" % self._layer_id
        code += "\n"                
        code += "initial = tf.constant(0.1, shape=[%s])\n" % self._feature_maps
        code += "b = tf.Variable(initial, name='bias-%s')\n" % self._layer_id
        code += "\n"        
        code += "node = tf.nn.conv1d(X['Y'], W, %s, padding=%s)\n" % (self._stride, self._padding)
        return code

    def _get_code_2d(self):
        code  = "shape = [%s, %s, X['Y'].get_shape().as_list()[-1], %s]\n" % (self._patch_size, self._patch_size, self._feature_maps)
        code += "initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(%s**2 + %s)))\n" % (self._patch_size, self._feature_maps)
        code += "W = tf.Variable(initial, name='weights-%s')\n" % self._layer_id        
        code += "\n"                
        code += "initial = tf.constant(0.1, shape=[%s])\n" % self._feature_maps
        code += "b = tf.Variable(initial, name='bias-%s')\n" % self._layer_id        
        code += "\n"        
        code += "node = tf.nn.conv2d(X['Y'], W, strides=[1, %s, %s, 1], padding=%s)\n" % (self._stride, self._stride, self._padding)
        return code
    
    def _get_code_3d(self):
        code  = "shape = [%s, %s, %s, X['Y'].get_shape().as_list()[-1], %s]\n" % (self._patch_size, self._patch_size, self._patch_size, self._feature_maps)
        code += "initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(%s**2 + %s)))\n" % (self._patch_size, self._feature_maps)
        code += "W = tf.Variable(initial, name='weights-%s')\n" % self._layer_id                
        code += "\n"        
        code += "initial = tf.constant(0.1, shape=[%s])\n" % self._feature_maps
        code += "b = tf.Variable(initial, name='bias-%s')\n" % self._layer_id                
        code += "\n"        
        code += "node = tf.nn.conv3d(X['Y'], W, strides=[1, %s, %s, %s, 1], padding=%s)\n" % (self._stride, self._stride, self._stride, self._padding)
        return code
    
    def _get_code_autodim(self):
        code  = "dim = str(len(X['Y'.get_shape().as_list())-1)\n"
        code += "shape = [%s]*dim + [X['Y'].get_shape().as_list()[-1]], %s]\n" % (self._patch_size, self._feature_maps)
        code += "initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(%s**2 + %s)))\n" % (self._patch_size, self._feature_maps)
        code += "W = tf.Variable(initial, name='weights-%s')\n" % self._layer_id                     
        code += "\n"                
        code += "initial = tf.constant(0.1, shape=[%s])\n" % self._feature_maps
        code += "b = tf.Variable(initial, name='bias-%s')\n" % self._layer_id                        
        code += "\n"        
        code += "node = tf.nn.conv2d(X['Y'], W, strides=[1]+[%s]*dim+[1], padding=%s)\n" % (self._stride, self._padding)
        return code


class TrainNormalCodeGenerator(CodeGenerator):
    def __init__(self, output_layer, target_layer,
                 n_epochs, n_iterations,
                 optimizer='adam', learning_rate=0.001):
        self._output_layer = output_layer
        self._target_layer = target_layer
        self._optimizer = optimizer
        self._learning_rate = learning_rate
        self._n_epochs = int(n_epochs)
        self._n_iters = int(n_iterations)

    def _get_training_code(self, mode):
        if self._optimizer == 'adam':
            opt_class = 'AdamOptimizer'
        elif self._optimizer == 'adagrad':
            opt_class = 'AdagradOptimizer'

        code  = ""
        code += "y_pred = X['%s']['Y']\n" % self._output_layer
        code += "y_label = X['%s']['Y']\n" % self._target_layer      
        code += "loss = tf.reduce_mean(tf.square(y_pred - y_label))\n"
        code += "step = tf.train.%s(learning_rate=%f).minimize(loss)\n" % (opt_class, self._learning_rate)
        code += "\n"
        code += "# Metrics\n"
        code += "correct_predictions = tf.equal(tf.argmax(y_pred), tf.argmax(y_label))\n"
        code += "accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32))\n"
        code += "f1, _ = tf.contrib.metrics.f1_score(y_label, y_pred)\n"
        code += "auc, _ = tf.metrics.auc(labels=y_label, predictions=y_pred, curve='ROC')\n"
        code += "\n"

        if mode != 'headless':
            code += "# Gradients\n"
            code += "gradients = {}\n"
            code += "for var in tf.trainable_variables():\n"
            code += "    name = 'grad-' + var.name\n"
            code += "    gradients[name] = tf.gradients(loss, [var])\n"
            code += "\n"


        code += "# Get iterators\n"
        code += "ops = tf.get_default_graph().get_operations()\n"
        code += "train_iterators = [op for op in ops if 'train_iterator' in op.name]\n"
        code += "validation_iterators = [op for op in ops if 'validation_iterator' in op.name]\n"
        code += "test_iterators = [op for op in ops if 'test_iterator' in op.name]\n"                
        code += "\n"
        code += "sess = tf.InteractiveSession()\n"
        code += "api.data.store_session(sess)\n"
        code += "init = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())\n"
        code += "sess.run(init)\n"
        code += "\n"
        code += "api.data.store(max_epoch=%d,\n" % (self._n_epochs - 1)
        code += "               max_iter_training=%d,\n" % (self._n_iters - 1)
        code += "               max_iter_validation=%d)\n" % (self._n_iters - 1)
        code += "\n"
        code += "for epoch in range(%d):\n" % self._n_epochs
        code += "    sess.run(train_iterators)\n"
        code += "    api.data.store(iter_training=0, iter_validation=0)\n"
        code += "    #Setting the variables to empty as a way to reset them every epoch.\n"
        code += "    api.data.store(acc_train_iter=[], loss_train_iter=[], f1_train_iter=[], auc_train_iter=[],\n" 
        code += "                   acc_val_iter=[], loss_val_iter=[], f1_val_iter=[], auc_val_iter=[])\n"
        code += "    \n"
        code += "    for iter in range(%d):\n" % self._n_iters
        code += "        sess.run(step)\n"
        code += "        acc_train, loss_train, f1_train, auc_train = sess.run([accuracy, loss, f1, auc])\n"
        code += "        api.data.stack(acc_train_iter=acc_train, loss_train_iter=loss_train, f1_train_iter=f1_train, auc_train_iter=auc_train)\n"
        code += "        api.data.store(iter_training=iter)\n"
        
        
        if mode != 'headless':
            code += "        gradient_vals = sess.run(gradients)\n"
            code += "        for grandName, gradValue in gradient_vals:\n"
            code += "            api.data.stack(gradName={;in: np.min(np.min(gradValue)), Max: np.max(np.max(gradValue)), Average: np.average(gradValue)})\n"
            #code += "        api.data.stack(**gradient_vals)\n"

        code += "        api.data.store_locals(locals())\n" 
        code += "        api.ui.render(dashboard='train_val')\n"
        code += "    \n"
        code += "    sess.run(validation_iterators)\n"        
        code += "    for iter in range(%d):\n" % self._n_iters
        code += "        loss_ = sess.run(loss)\n"
        code += "        acc_val, loss_val, f1_val, auc_val = sess.run([accuracy, loss, f1, auc])\n"
        code += "        api.data.stack(acc_val_iter=acc_val, loss_val_iter=loss_val, f1_val_iter=f1_val, auc_val_iter=auc_val)\n"
        code += "        api.data.store(iter_validation=iter)\n"
        code += "        api.ui.render(dashboard='train_val')\n"        
        code += "    \n"
        code += "    api.data.store(epoch=epoch)\n"
        code += "    api.data.stack(acc_training_epoch=acc_train, loss_train_epoch=loss_train, f1_training_epoch=f1_train, auc_training_epoch=auc_train,\n"
        code += "                   acc_validation_epoch=acc_val, loss_val_epoch=loss_val, f1_validation_epoch=f1_val, auc_validation_epoch=auc_val)\n"
        code += "    api.ui.render(dashboard='train_val')\n"
        return code

    def _get_testing_code(self, mode):
        code  = "api.data.store(max_iter_testing=%d)\n" % (self._n_iters - 1)
        code += "sess.run(test_iterators)\n"                
        code += "for iter in range(%d):\n" % self._n_iters
        code += "    y_pred_ = sess.run(y_pred)\n"
        code += "    api.data.stack(y_pred=y_pred_.squeeze())\n"
        code += "    api.data.store(iter_testing=iter)\n"
        code += "    api.ui.render(dashboard='testing')\n"        
        return code

    def get_code_parts(self, mode='normal'):
        cp1 = CodePart('training', self._get_training_code(mode))
        cp2 = CodePart('testing', self._get_testing_code(mode))
        return [cp1, cp2] # TODO: Should probably be dicts?

    def get_code(self, mode='normal'):
        code = self._get_training_code(mode) + '\n' + self._get_testing_code(mode)
        return code
