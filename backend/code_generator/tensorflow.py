from collections import namedtuple

from code_generator import CodeGenerator, CodePart


def get_activation_code(var_in, var_out, func=None):
    if func is None or func == 'None':
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
        
    def get_code(self):
        shape_text = ', '.join([str(i) for i in self._shape])
        perm_text = ', '.join([str(i) for i in self._permutation])
        code = ""
        code += "Y=tf.reshape(X['Y'], [-1]+[layer_output for layer_output in [%s]])\n" % shape_text
        code += "Y=tf.transpose(Y,perm=[0]+[i+1 for i in [%s]])\n" % perm_text
        return code

    
class RecurrentCodeGenerator(CodeGenerator):
    def __init__(self, version, time_steps, neurons, return_sequences=False, dropout=False, keep_prop=1):
        self._version = version
        self._time_steps = time_steps
        self._neurons = neurons
        self._return_sequences = return_sequences
        self._dropout=dropout
        self._keep_prob=keep_prop

    def get_code(self):
        code = ''
        if self._version == 'LSTM':
            code += "cell = tf.nn.rnn_cell.LSTMCell(%s, state_is_tuple=True)\n" % self._neurons
        elif self._version == 'GRU':
            code += "cell = tf.nn.rnn_cell.GRUCell(%s, state_is_tuple=True)\n" % self._neurons
        elif self._version == 'RNN':
            code += "cell = tf.nn.rnn_cell.BasicRNNCell(%s, state_is_tuple=True)\n" % self._neurons

        if self._dropout:
            code += "cell = tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=%s)" % self._keep_prob
            
        code += "node = X['Y']\n"
        code += "rnn_outputs, final_state = tf.nn.dynamic_rnn(cell, node, dtype=node.dtype)\n"
        
        if self._return_sequences:
            code += "Y = rnn_outputs\n"
        else:
            code += "Y = rnn_outputs[:, -1]\n"
            
        return code
    

class WordEmbeddingCodeGenerator(CodeGenerator):
    def get_code(self):
        code  = "words = tf.string_split(X['Y'])\n"
        code += 'vocab_size=words.get_shape().as_list()[0]\n'
        code += 'embed_size=10\n'
        code += 'embedding = tf.Variable(tf.random_uniform((vocab_size, embed_size), -1, 1))\n'
        code += "Y = tf.nn.embedding_lookup(embedding, X['Y'])\n"
        return code


class OneHotCodeGenerator(CodeGenerator):
    def __init__(self, n_classes):
        self._n_classes = n_classes
        
    def get_code(self):
        code = "Y=tf.one_hot(tf.cast(X['Y'],dtype=tf.int32), %s)\n" % self._n_classes
        return code

    
class CropCodeGenerator(CodeGenerator):
    def __init__(self, offset_values, target_values):
        self.offset_values = offset_values
        self.target_values = target_values #max - min   

    def get_code(self):
        shape = X['Y'].get_shape().as_list()
        code = "Y = X['Y'][:,:,"
        for i in range(len(shape)-2):
            code += "%d:%d+%d, "%(self.offset_values[i], self.target_values[i], self.offset_values[i])
            code += "]\n"
        return code


class ResizeCodeGenerator(CodeGenerator):
    def __init__(self, resize_width, resize_height):
        self.resize_width = resize_width
        self.resize_height = resize_height

    def get_code(self):
        code = "Y = tf.image.resize_images(X['Y'][:], [%d, %d], method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)\n"%(self.resize_width, self.resize_height)
        return code

    
class GrayscaleCodeGenerator(CodeGenerator):
    def get_code(self):
        code  = "if X['Y'].get_shape().as_list()[-1] == 3:\n"
        code += "    Y = tf.image.rgb_to_grayscale(X['Y'])\n"
        code += 'else:\n'
        code += "    Y = X['Y']\n"
        return code


class ArgmaxCodeGenerator(CodeGenerator):
    def __init__(self, dim):
        self._dim = dim

    def get_code(self):
        code = "Y = tf.argmax(X['Y'], %s)" % self._dim
        return code


class SoftmaxCodeGenerator(CodeGenerator):
    def get_code(self):
        code = "Y = tf.nn.softmax(X['Y'])"
        return code


class MergeCodeGenerator(CodeGenerator):
    def __init__(self, type_, merge_dim):
        self._type = type_
        self._merge_dim = merge_dim

    def get_code(self):
        # TODO: in python version < 3.6 dicts aren't ordered. caution if we allow custom environments in the future.
        
        if self._type == 'Concat':
            # Due to duplicate values in X['Y'], just take every other value.            
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

    def get_code(self):
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

class DeconvCodeGenerator(CodeGenerator):
    def __init__(self, layer_id, conv_dim, feature_maps, stride, padding,
                 dropout=False, keep_prob=None, activation=None):
        self._layer_id = layer_id
        self._conv_dim = conv_dim
        self._feature_maps = feature_maps
        self._stride = stride
        self._padding = padding
        self._dropout = dropout
        self._keep_prob = keep_prob
        self._activation = activation

    def get_code(self):
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
       
        return code

    def _get_code_1d(self):
        code  = "shape = [%s, X['Y'].get_shape().as_list()[-1], %s]\n" % (self._stride, self._feature_maps)
        code += "initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(%s**2 + %s)))\n" % (self._stride, self._feature_maps)
        code += "W = tf.Variable(initial, name='weights-%s')\n" % self._layer_id
        code += "\n"                
        code += "initial = tf.constant(0.1, shape=[%s])\n" % self._feature_maps
        code += "b = tf.Variable(initial, name='bias-%s')\n" % self._layer_id
        code += "\n"    
        code += "output_shape=tf.stack([X['Y'].get_shape().as_list()[0]] + [node_shape*%s for node_shape in  X['Y'].get_shape().as_list()[1:-1]] + [%s])\n" %(self._stride, self._feature_maps)    
        code += "node = tf.nn.conv1d_transpose(X['Y'], W, output_shape, strides=%s, padding=%s)\n" % (self._stride, self._padding)
        return code

    def _get_code_2d(self):
        code  = "shape = [%s, %s, X['Y'].get_shape().as_list()[-1], %s]\n" % (self._stride, self._stride, self._feature_maps)
        code += "initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(%s**2 + %s)))\n" % (self._stride, self._feature_maps)
        code += "W = tf.Variable(initial, name='weights-%s')\n" % self._layer_id        
        code += "\n"                
        code += "initial = tf.constant(0.1, shape=[%s])\n" % self._feature_maps
        code += "b = tf.Variable(initial, name='bias-%s')\n" % self._layer_id        
        code += "\n"        
        code += "output_shape=tf.stack([X['Y'].get_shape().as_list()[0]] + [node_shape*%s for node_shape in  X['Y'].get_shape().as_list()[1:-1]] + [%s])\n" %(self._stride, self._feature_maps)    
        code += "node = tf.nn.conv2d_transpose(X['Y'], W, output_shape, strides=[1, %s, %s, 1], padding=%s)\n" % (self._stride, self._stride, self._padding)
        return code

    def _get_code_3d(self):
        code  = "shape = [%s, %s, %s, X['Y'].get_shape().as_list()[-1], %s]\n" % (self._stride, self._stride, self._stride, self._feature_maps)
        code += "initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(%s**2 + %s)))\n" % (self._stride, self._feature_maps)
        code += "W = tf.Variable(initial, name='weights-%s')\n" % self._layer_id                
        code += "\n"        
        code += "initial = tf.constant(0.1, shape=[%s])\n" % self._feature_maps
        code += "b = tf.Variable(initial, name='bias-%s')\n" % self._layer_id                
        code += "\n"        
        code += "output_shape=tf.stack([X['Y'].get_shape().as_list()[0]] + [node_shape*%s for node_shape in  X['Y'].get_shape().as_list()[1:-1]] + [%s])\n" %(self._stride, self._feature_maps)
        code += "node = tf.nn.conv3d_transpose(X['Y'], W, output_shape, strides=[1, %s, %s, %s, 1], padding=%s)\n" % (self._stride, self._stride, self._stride, self._padding)
        return code
    
    def _get_code_autodim(self):
        code  = "dim = str(len(X['Y'.get_shape().as_list())-1)\n"
        code += "shape = [%s]*dim + [X['Y'].get_shape().as_list()[-1]], %s]\n" % (self._stride, self._feature_maps)
        code += "initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(%s**2 + %s)))\n" % (self._stride, self._feature_maps)
        code += "W = tf.Variable(initial, name='weights-%s')\n" % self._layer_id                     
        code += "\n"                
        code += "initial = tf.constant(0.1, shape=[%s])\n" % self._feature_maps
        code += "b = tf.Variable(initial, name='bias-%s')\n" % self._layer_id                        
        code += "\n"    
        code += "output_shape=tf.stack([X['Y'].get_shape().as_list()[0]] + [node_shape*%s for node_shape in  X['Y'].get_shape().as_list()[1:-1]] + [%s])\n" %(self._stride, self._feature_maps)    
        code += "node = tf.nn.conv2d(X['Y'], W, output_shape, strides=[1]+[%s]*dim+[1], padding=%s)\n" % (self._stride, self._padding)
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

    def get_code(self):
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

class TrainLossCodeGenerator(CodeGenerator):
    def __init__(self, output_layer, target_layer, loss_function, class_weights = 1):
        self._output_layer = output_layer
        self._target_layer = target_layer
        self._loss_function = loss_function
        self._class_weights = str(class_weights)

    def get_loss_code(self):
        code = ""
        code += "y_pred = X['%s']['Y']\n" % self._output_layer
        code += "y_label = X['%s']['Y']\n" % self._target_layer  
        if self._loss_function == "Cross_entropy":
            code += "n_classes = y_pred.get_shape().as_list()[-1]\n"
            code += "flat_pred = tf.reshape(y_pred, [-1, n_classes])\n"
            code += "flat_labels = tf.reshape(y_label, [-1, n_classes])\n"
            code += "loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=flat_labels, logits=flat_pred))\n"

        elif self._loss_function == "Quadratic":
            code += "loss = tf.reduce_mean(tf.square(y_pred - y_label))\n"

        elif self._loss_function == "Regression":
            code += "loss = tf.reduce_mean(tf.square(y_pred - y_label))\n"

        elif self._loss_function == "W_cross_entropy":
            code += "n_classes = y_pred.get_shape().as_list()[-1]\n"
            code += "flat_pred = tf.reshape(y_pred, [-1, n_classes])\n"
            code += "flat_labels = tf.reshape(y_label, [-1, n_classes])\n"
            code += "loss =  tf.reduce_mean(tf.nn.weighted_cross_entropy_with_logits(flat_labels, flat_pred, %s))\n" % self._class_weights

        elif self._loss_function == "Dice":
            code += "eps = 1e-5\n"
            code += "intersection = tf.reduce_sum(tf.multiply(y_pred, y_label))\n"
            code += "union = eps + tf.reduce_sum(tf.multiply(y_pred, y_pred)) + tf.reduce_sum(tf.multiply(y_label, y_label))\n"
            code += "cost_tmp = (2 * intersection/union)\n"
            code += "cost_clip = tf.clip_by_value(cost_tmp, eps, 1.0-eps)\n"
            code += "loss = 1 - cost_clip\n"

        elif self._loss_function == "None":
            pass

        else:
            raise NotImplementedError("The Loss you tried to use is not yet implemented")

        return code
    def get_code(self):
        code=self.get_loss_code()
        code += "Y=loss\n"
        return code

class TrainOptimizerCodeGenerator(CodeGenerator):
    def __init__(self, optimizer, learning_rate=0.001, decay_steps=100000, decay_rate=0.96, momentum=0.9, beta1=0.9, beta2=0.999):
        self._optimizer = optimizer
        self._learning_rate = str(learning_rate)
        self._decay_steps = str(decay_steps)
        self._decay_rate = str(decay_rate)
        self._momentum = str(momentum)
        self._beta1 = str(beta1)
        self._beta2 = str(beta2)

    def get_optimizer_code(self):
        code = ""
        if self._optimizer == 'SGD':
            code += "step = tf.train.GradientDescentOptimizer(learning_rate=%s).minimize(loss)\n" % self._learning_rate
        elif self._optimizer == 'Momentum':
            code += "global_step = tf.Variable(0)\n"
            code += "learning_rate_momentum = tf.train.exponential_decay(learning_rate=%s, global_step=global_step, decay_steps=%s, decay_rate=%s, staircase=True)\n" % (self._learning_rate, self._decay_steps, self._decay_rate)
            code += "step = tf.train.MomentumOptimizer(learning_rate=learning_rate_momentum, momentum=%s).minimize(loss, global_step=global_step)\n" % self._momentum
        elif self._optimizer == "ADAM":
            code += "step = tf.train.AdamOptimizer(learning_rate=%s,beta1=%s,beta2=%s).minimize(loss)\n" % (self._learning_rate, self._beta1, self._beta2)
        elif self._optimizer == "adagrad":
            code += "step = tf.train.AdagradOptimizer(learning_rate=%s).minimize(loss)\n" % self._learning_rate
        elif self._optimizer == "RMSprop":
            code += "step = tf.train.RMSPropOptimizer(learning_rate=%s).minimize(loss)\n" % self._learning_rate
        elif self._optimizer == "None":
            pass
        else:
            raise NotImplementedError("The Optimizer you tried to use is not yet implemented")
        return code

    def get_code(self):
        code = "loss=X['Y']\n"
        code += self.get_optimizer_code()
        code += "Y=step\n"
        return code


class TrainNormalCodeGenerator(CodeGenerator):
    def __init__(self, output_layer, target_layer,
                 n_epochs,
                 loss_function='Quadratic', class_weights = 1,
                 optimizer='ADAM', learning_rate=0.001, decay_steps=100000, decay_rate=0.96, momentum=0.9, beta1=0.9, beta2=0.999):
        self._output_layer = output_layer
        self._target_layer = target_layer
        self._n_epochs = int(n_epochs)
        #Loss
        self._loss_function = loss_function
        self._class_weights = class_weights
        #Optimizer
        self._optimizer = optimizer
        self._learning_rate = learning_rate
        self._decay_steps = decay_steps
        self._decay_rate = decay_rate
        self._momentum = momentum
        self._beta1 = beta1
        self._beta2 = beta2
        

    def _get_training_code(self):
        code  = ""
        code += TrainLossCodeGenerator(self._output_layer, self._target_layer, self._loss_function, self._class_weights).get_loss_code()
        code += "# Gradients\n"
        code += "gradients = {}\n"
        code += "for var in tf.trainable_variables():\n"
        code += "    name = 'grad-' + var.name\n"
        code += "    gradients[name] = tf.gradients(loss, [var])\n"
        code += "\n"
        code += TrainOptimizerCodeGenerator(self._optimizer,self._learning_rate, self._decay_steps, self._decay_rate, self._momentum, self._beta1, self._beta2).get_optimizer_code()
        code += "\n"
        code += "# Metrics\n"
        code += "correct_predictions = tf.equal(tf.argmax(y_pred,-1), tf.argmax(y_label,-1))\n"
        code += "accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32))\n"
        if self._loss_function == "Regression":
            code += "f1 = tf.constant(0)\n"
            code += "auc = tf.constant(0)\n"
        else:
            code += "f1, _ = tf.contrib.metrics.f1_score(y_label, y_pred)\n"
            code += "auc, _ = tf.metrics.auc(labels=y_label, predictions=y_pred, curve='ROC')\n"
        code += "\n"
        code += "# Get iterators\n"
        code += "ops = tf.get_default_graph().get_operations()\n"
        code += "train_iterators = [op for op in ops if 'train_iterator' in op.name]\n"
        code += "validation_iterators = [op for op in ops if 'validation_iterator' in op.name]\n"
        code += "test_iterators = [op for op in ops if 'test_iterator' in op.name]\n" 
        code += "#tf variables to be evaluated and sent to the frontend\n"    
        code += "\n"
        code += "sess = tf.InteractiveSession()\n"
        code += "saver = tf.train.Saver()\n"
        code += "api.data.setSaver(sess,saver)\n"
        code += "init = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())\n"
        code += "sess.run(init)\n"
        code += "api.data.store_locals(locals())\n"
        code += "all_tensors=api.data.get_tensors()\n" 
        code += "api.data.store(all_tensors=all_tensors)\n"
        code += "import time\n"
        code += "\n"
        code += "api.data.store(max_epoch=%d,\n" % (self._n_epochs - 1)
        code += "               train_datasize=_data_size[0],\n"
        code += "               val_datasize=_data_size[1])\n"
        code += "\n"
        code += "for epoch in range(%d):\n" % self._n_epochs
        code += "    startTime=time.time()\n"
        code += "    sess.run(train_iterators)\n"
        code += "    api.data.store(iter_training=0, iter_validation=0)\n"
        code += "    #Setting the variables to empty as a way to reset them every epoch.\n"
        code += "    api.data.store(acc_train_iter=[], loss_train_iter=[], f1_train_iter=[], auc_train_iter=[],\n" 
        code += "                   acc_val_iter=[], loss_val_iter=[], f1_val_iter=[], auc_val_iter=[])\n"
        code += "    \n"
        code += "    train_iter=0\n"
        code += "    try:\n"
        code += "        while True:\n"
        code += "            if api.ui.headless:\n"
        code += "                _, acc_train, loss_train, f1_train, auc_train = sess.run([step, accuracy, loss, f1, auc])\n"
        code += "            else:\n"
        code += "                _, acc_train, loss_train, f1_train, auc_train, gradient_vals, all_evaled_tensors = sess.run([step, accuracy, loss, f1, auc, gradients, all_tensors])\n"
        code += "                api.data.store(all_evaled_tensors=all_evaled_tensors)\n"
        
        code += "                new_gradient_vals={}\n"
        code += "                for gradName, gradValue in gradient_vals.items():\n"
        code += "                     new_gradient_vals[gradName+':Min'] = np.min(np.min(gradValue))\n"
        code += "                     new_gradient_vals[gradName+':Max'] = np.max(np.max(gradValue))\n"
        code += "                     new_gradient_vals[gradName+':Average'] = np.average(gradValue)\n"
        code += "                api.data.stack(**new_gradient_vals)\n"
        
        code += "            api.data.stack(acc_train_iter=acc_train, loss_train_iter=loss_train, f1_train_iter=f1_train, auc_train_iter=auc_train)\n"
        code += "            api.data.store(iter_training=train_iter)\n"

        code += "            api.ui.render(dashboard='train_val')\n"
        code += "            train_iter+=1\n"
        code += "    except tf.errors.OutOfRangeError:\n"
        code += "        pass\n"
        code += "    \n"
        code += "    sess.run(validation_iterators)\n"    
        code += "    val_iter=0\n"    
        code += "    try:\n"
        code += "        while True:\n"
        code += "            if api.ui.skip:\n"
        code += "                api.ui.skip=False\n"
        code += "                break\n"
        code += "            \n"
        code += "            if api.ui.headless:\n"
        code += "                _, acc_val, loss_val, f1_val, auc_val = sess.run([step, accuracy, loss, f1, auc])\n"
        code += "            else:\n"
        code += "                _, acc_val, loss_val, f1_val, auc_val, gradient_vals, all_evaled_tensors = sess.run([step, accuracy, loss, f1, auc, gradients, all_tensors])\n"
        code += "                api.data.store(all_evaled_tensors=all_evaled_tensors)\n"
        
        code += "                new_gradient_vals={}\n"
        code += "                for gradName, gradValue in gradient_vals.items():\n"
        code += "                     new_gradient_vals[gradName+':Min'] = np.min(np.min(gradValue))\n"
        code += "                     new_gradient_vals[gradName+':Max'] = np.max(np.max(gradValue))\n"
        code += "                     new_gradient_vals[gradName+':Average'] = np.average(gradValue)\n"
        code += "                api.data.stack(**new_gradient_vals)\n"

        code += "            api.data.stack(acc_val_iter=acc_val, loss_val_iter=loss_val, f1_val_iter=f1_val, auc_val_iter=auc_val)\n"
        code += "            api.data.store(iter_validation=val_iter)\n"
        code += "            api.ui.render(dashboard='train_val')\n"  
        code += "            val_iter+=1\n" 
        code += "    except tf.errors.OutOfRangeError:\n"
        code += "        pass\n"    
        code += "    \n"
        code += "    api.data.store(epoch=epoch)\n"
        code += "    print('Epoch: %d Acc: %f Loss: %f' %(epoch, acc_train, loss_train))\n"
        code += "    api.data.stack(acc_training_epoch=acc_train, loss_training_epoch=loss_train, f1_training_epoch=f1_train, auc_training_epoch=auc_train,\n"
        code += "                   acc_validation_epoch=acc_val, loss_validation_epoch=loss_val, f1_validation_epoch=f1_val, auc_validation_epoch=auc_val)\n"
        code += "    api.ui.render(dashboard='train_val')\n"
        code += "    endTime=time.time()-startTime\n"
        code += "    print('Time: %f' %(endTime))\n"
        code += "    import sys\n"
        code += "    print('Size: %f' %(sys.getsizeof(str(all_evaled_tensors))) \n)"
        return code


    def _get_testing_code(self):
        code  = "api.data.store(max_iter_testing=_data_size[2])\n"
        code += "sess.run(test_iterators)\n"     
        code += "iter = 0\n"
        code += "try:\n"
        code += "    while True:\n"
        code += "        all_evaled_tensors = sess.run(all_tensors)\n"
        code += "        api.data.store(all_tensors=all_evaled_tensors)\n"
        code += "        api.data.store(iter_testing=iter)\n"
        code += "        iter+=1\n"
        code += "        api.ui.render(dashboard='testing')\n"  
        code += "except tf.errors.OutOfRangeError:\n"      
        code += "    pass\n"
        return code

    def get_code_parts(self):
        cp1 = CodePart('training', self._get_training_code())
        cp2 = CodePart('testing', self._get_testing_code())
        return [cp1, cp2] # TODO: Should probably be dicts?

    def get_code(self):
        code = self._get_training_code() + '\n' + self._get_testing_code()
        print(code)
        return code


LayerPair = namedtuple('LayerPair', ['online_id', 'target_id'])



class TrainReinforceCodeGenerator(CodeGenerator):
    def __init__(self, online_network_id, target_network_id, layer_pairs, n_episodes=20000, history_length=2, batch_size=32, learning_rate=0.1, discount_factor=0.99,
                 replay_start_size=1000, replay_memory_size=300000,
                 initial_exploration=0.9, final_exploration=0.1,
                 update_frequency=4, target_network_update_frequency=100):
        self._batch_size = batch_size                
        self._n_episodes = n_episodes
        self._history_length = history_length
        self._replay_start_size = replay_start_size        
        self._replay_memory_size = replay_memory_size
        self._learning_rate = learning_rate
        self._gamma = discount_factor
        self._update_frequency = update_frequency
        self._copy_weights_frequency = target_network_update_frequency
        self._n_steps_max = 1000

        self._online_network_id = online_network_id# #"'1'"
        self._target_network_id = target_network_id# "'2'"
        self._layer_pairs = layer_pairs# [LayerPair('11', '21')]#, LayerPair('12', '22')]
        
        
    def get_code(self):
        code  = "global state_tensor, env\n"
        code += "Q_online = X['%s']['Y']\n" % self._online_network_id
        code += "Q_target = X['%s']['Y']\n" % self._target_network_id                
        code += "\n"
        code += "# Constants\n"
        code += "gamma = %f\n" % self._gamma
        code += "batch_size = %d\n" % self._batch_size
        code += "history_length = %d\n" % self._history_length
        code += "replay_start_size = %d\n" % self._replay_start_size
        code += "n_actions = env.action_space.n\n"
        code += "n_steps_max = %d\n" % self._n_steps_max
        code += "n_episodes = %d\n" % self._n_episodes
        code += "api.data.store(n_steps_max=n_steps_max, n_episodes=n_episodes, batch_size=batch_size, n_actions=n_actions)\n"
        code += "\n"
        code += "# Exploration/exploitation tradeoff\n" # TODO: name
        code += "def epsilon(episode):\n"
        code += "    #eps = 1/np.sqrt(1 + episode)\n"
        code += "    eps = 0.9**(episode/500)\n"
        code += "    eps = max(0.1, eps)\n"
        code += "    return eps\n"
        code += "\n"
        code += "# Optimizer\n"
        code += "input_shape = state_tensor.get_shape().as_list()[1:]\n" # TODO: fix this!
        code += "y_tensor = tf.placeholder(tf.float32, [None, 1], name='y')\n"
        code += "a_tensor = tf.placeholder(tf.uint8, [None, 1], name='a')\n"
        code += "\n"
        code += "a_one_hot = tf.one_hot(a_tensor, n_actions, dtype=tf.float32)\n"
        code += "a_one_hot = a_one_hot[:, -1, :]\n" # Remove extra dimension => (batch_size, n_actions)
        code += "q_performed = tf.reduce_sum(tf.multiply(Q_online, a_one_hot), axis=1, keep_dims=True)\n"
        code += "loss_tensor = tf.reduce_mean(tf.square(y_tensor - q_performed))\n"
        code += "optimizer = tf.train.AdamOptimizer(learning_rate=%f)\n" % self._learning_rate
        code += "step = optimizer.minimize(loss_tensor)\n"
        code += "\n"

        code += "# Gradients\n"
        code += "gradients = {}\n"
        code += "for var in tf.trainable_variables():\n"
        code += "    name = 'grad-' + var.name\n"
        code += "    gradient_tensor = tf.gradients(loss_tensor, [var])\n"
        code += "    if gradient_tensor[0] is not None:\n" # Without an explicit dependence, the derivative should be 0.
        code += "        gradients[name] = gradient_tensor \n"
        code += "\n"
        code += "new_gradient_vals = None\n"


        code += "def copy_weights(sess):\n"
        code += "    variables = {var.op.name: var for var in tf.trainable_variables()}\n"
        code += "    update_ops = []\n"        
        for pair in self._layer_pairs:
            code += "    if 'weights-%s' in variables:\n" % pair.online_id
            code += "        W_online = variables['weights-%s']\n" % pair.online_id
            code += "        W_target = variables['weights-%s']\n" % pair.target_id
            code += "        update_ops.append(W_target.assign(W_online))\n"
            code += "        b_online = variables['bias-%s']\n" % pair.online_id
            code += "        b_target = variables['bias-%s']\n" % pair.target_id
            code += "        update_ops.append(b_target.assign(b_online))\n"
            code += "    \n"
        code += "    \n"
        code += "    sess.run(update_ops)\n"
        code += "sess = tf.InteractiveSession()\n"
        code += "init = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())\n"
        code += "sess.run(init)\n"
        code += "\n"                
        code += "copy_weights(sess)\n"

        code += "api.data.store_locals(locals())\n"
        code += "all_tensors=api.data.get_tensors()\n" 
        
        code += "\n"
        code += "# Run training\n"
        code += "replay_memory_size = %d\n" % self._replay_memory_size
        code += "replay_memory = []\n" 
        code += "\n"
        code += "iteration = 0\n"
        code += "for episode in range(n_episodes):\n"
        code += "    state = env.reset()\n"
        code += "    state_seq = [state]*history_length\n"
        code += "    api.data.store(episode=episode)\n"
        code += "    \n"
        code += "    done = False\n"
        code += "    step_counter = 0\n"
        code += "    loss_list = []\n"
        code += "    reward_list = []\n"        
        code += "    while not done and step_counter < n_steps_max:\n"
        code += "        explore = np.random.random() < epsilon(episode) or iteration < replay_start_size\n"
        code += "        if explore:\n"
        code += "            action = env.action_space.sample()\n"
        code += "            Q = Q_online.eval(feed_dict={state_tensor: np.array([state_seq])}).squeeze()\n"
        code += "        else:\n"
        code += "            Q = Q_online.eval(feed_dict={state_tensor: np.array([state_seq])}).squeeze()\n"
        code += "            action = np.argmax(Q)\n"
        code += "        \n"
        code += "        new_state, reward, done, info = env.step(action)\n"
        code += "        new_state_seq = state_seq[1:] + [new_state]\n"
        code += "        reward_list.append(reward)\n"
        code += "        api.data.store(current_state=state, current_action=action, step_counter=step_counter)\n"
        code += "        api.data.store(reward=np.cumsum(reward_list))\n"
        code += "        api.ui.render(dashboard='train_reinforce')\n"
        code += "        \n"
        code += "        # Remember transition\n"
        code += "        transition = {\n"
        code += "                      'state_seq': np.array(state_seq),\n"
        code += "                      'new_state_seq': np.array(new_state_seq),\n"
        code += "                      'action': action,\n"
        code += "                      'reward': reward,\n"
        code += "                      'done': done\n"         
        code += "                      }\n"
        code += "        #if reward > 0:\n"
        code += "        replay_memory.append(transition)\n"
        code += "        if len(replay_memory) > replay_memory_size:\n"
        code += "            replay_memory.pop(0)\n"
        code += "        \n"
        code += "        state_seq = new_state_seq\n"        
        code += "        # Training\n"
        code += "        \n"
        code += "        if iteration % {} == 0 and iteration > replay_start_size:\n".format(self._update_frequency) # TODO: better name for n_iters
        code += "            batch_transitions = np.random.choice(replay_memory, batch_size)\n"
        code += "            y_batch = np.zeros((batch_size, 1))\n"
        code += "            a_batch = np.zeros((batch_size, 1))\n" 
        code += "            X_batch = np.zeros((batch_size,) + tuple(input_shape))\n"
        code += "            \n"
        code += "            for i, t in enumerate(batch_transitions):\n"
        code += "                y_batch[i] = t['reward']\n"
        code += "                if not t['done']:\n"
        code += "                    feed_dict = {state_tensor: [t['new_state_seq']]}\n"
        code += "                    Q = Q_target.eval(feed_dict=feed_dict).squeeze()\n" 
        code += "                    y_batch[i] += gamma*np.amax(Q)\n"
        code += "                a_batch[i] = t['action']\n"
        code += "                X_batch[i] = t['state_seq']\n"
        code += "            \n"
        code += "            feed_dict = {\n"
        code += "                         state_tensor: np.atleast_2d(X_batch),\n"
        code += "                         a_tensor: np.atleast_2d(a_batch),\n"
        code += "                         y_tensor: np.atleast_2d(y_batch),\n"
        code += "                        }\n"
        code += "            _, loss, gradient_vals, all_tensors_values = sess.run([step, loss_tensor, gradients, all_tensors], feed_dict=feed_dict)\n"
        code += "            loss_list.append(loss)\n"
        code += "            api.data.store(loss=loss_list)\n"
        code += "            api.data.store(all_tensors=all_tensors_values)\n"

        code += "            new_gradient_vals={}\n"
        code += "            for gradName, gradValue in gradient_vals.items():\n"
        code += "                new_gradient_vals[gradName+':Min'] = np.min(np.min(gradValue))\n"
        code += "                new_gradient_vals[gradName+':Max'] = np.max(np.max(gradValue))\n"
        code += "                new_gradient_vals[gradName+':Average'] = np.average(gradValue)\n"

        code += "        if new_gradient_vals is not None:\n"
        code += "            api.data.stack(**new_gradient_vals)\n"
        code += "        \n"
        code += "        # Copy weights\n"
        code += "        if iteration % {} == 0:\n".format(self._copy_weights_frequency)
        code += "            copy_weights(sess)\n"
        code += "        iteration += 1\n"
        code += "        step_counter += 1\n"
        code += "        state = new_state\n"
        code += "    api.data.stack(episode_reward=np.sum(reward_list))\n"
        code += "    api.data.stack(episode_steps=step_counter)\n"        
        code += "    if len(loss_list) > 0:\n"
        code += "        api.data.stack(episode_loss=loss_list[-1])\n"        

        return code

    
import gym
import copy
import numpy as np
import random
class DummyEnv(gym.Env):

    def __init__(self):
        self.action_space = gym.spaces.Discrete(4)
        self.observation_space = gym.spaces.Box(np.array([0]), np.array([1]))
        self.reset()
        
    def reset(self):
        self._has_entered = {
            'bot_right': False,           
            'top_right': False,
            'bot_left': False,                        
            'top_left': False
        }
        self._pos = 'bot_left'
        self._done = False
        self._actions = []
        return self._get_state()

    def step(self, action):
        if self._done:
            raise RuntimeError("Already done!")
        
        pos1 = self._pos
        
        if action == 0: # MOVE UP
            if self._pos == 'bot_left':
                self._pos = 'top_left'
            elif self._pos == 'bot_right':
                self._pos = 'top_right'
        elif action == 1: # MOVE RIGHT
            if self._pos == 'top_left':
                self._pos = 'top_right'
            elif self._pos == 'bot_left':
                self._pos = 'bot_right'
            
        elif action == 2: # MOVE DOWN
            if self._pos == 'top_left':
                self._pos = 'bot_left'
            elif self._pos == 'top_right':
                self._pos = 'bot_right'
        elif action == 3: # MOVE LEFT
            if self._pos == 'top_right':
                self._pos = 'top_left'
            elif self._pos == 'bot_right':
                self._pos = 'bot_left'            

        self._actions.append(action)
        self._done = len(self._actions) >= 4

        if self._actions == [0, 1, 2, 3]:
            # Reward only comes if all has been entered and if the first action was to move up
            reward = 100
        else:
            reward = -10

        state = self._get_state()
        return state, reward, self._done, {'actions': self._actions}

    def _get_state(self):
        state = np.zeros((2, 2))
        if self._pos == 'top_left':
            state[0, 0] = 1
        elif self._pos == 'bot_left':
            state[1, 0] = 1
        elif self._pos == 'top_right':
            state[0, 1] = 1
        elif self._pos == 'bot_right':
            state[1, 1] = 1
        return state
        
    def seed(self, seed):
        random.seed(seed)
        np.random.seed(seed)
    



    
if __name__ == "__main__":
    #import pdb; pdb.set_trace()

    
    import tensorflow as tf
    import numpy as np
    import gym

    np.random.seed(456)
    tf.set_random_seed(456)
    
    
    from unittest import mock
    api = mock.Mock()
    env = gym.make('Breakout-v0')    
    #env = DummyEnv()
    
    sample = env.reset()
    SEQ_SIZE = 2
    state_window_shape = (None, SEQ_SIZE, ) + sample.shape # [None, 4, 210, 160, 3]
    #print(state_window_shape)
    #raise SystemExit
    state_tensor = tf.placeholder(tf.float32, shape=state_window_shape, name='state_tensor')

    #import pdb; pdb.set_trace()

    # Online Network 
    N_NEURONS = 4 # n actions
    X = {'Y':  state_tensor}
    input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]
    shape = [input_size, N_NEURONS]
    initial = tf.truncated_normal(shape, stddev=0.1)
    W = tf.Variable(initial, name='weights-11')#\n" % self._layer_id
    initial = tf.constant(0.1, shape=[N_NEURONS])#\n" % self._n_neurons
    b = tf.Variable(initial, name='bias-11')#\n" % self._layer_id
    flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)
    node = tf.matmul(flat_node, W)    
    node = node + b
    Y1 = node

    '''
    X = {'Y':  Y1}
    input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]
    shape = [input_size, N_NEURONS]
    initial = tf.truncated_normal(shape, stddev=0.1)
    W = tf.Variable(initial, name='weights-12')#\n" % self._layer_id
    initial = tf.constant(0.1, shape=[N_NEURONS])#\n" % self._n_neurons
    b = tf.Variable(initial, name='bias-12')#\n" % self._layer_id
    flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)
    node = tf.matmul(flat_node, W)    
    node = node + b
    Y1 = tf.sigmoid(node)
    '''
    
    
    # Target Network 
    N_NEURONS = 4 # n actions
    X = {'Y':  state_tensor}
    input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]
    shape = [input_size, N_NEURONS]
    initial = tf.truncated_normal(shape, stddev=0.1)
    W = tf.Variable(initial, name='weights-21')#\n" % self._layer_id
    initial = tf.constant(0.1, shape=[N_NEURONS])#\n" % self._n_neurons
    b = tf.Variable(initial, name='bias-21')#\n" % self._layer_id
    flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)
    node = tf.matmul(flat_node, W)    
    node = node + b
    Y2 = node
    '''
    X = {'Y':  Y2}
    input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]
    shape = [input_size, N_NEURONS]
    initial = tf.truncated_normal(shape, stddev=0.1)
    W = tf.Variable(initial, name='weights-22')#\n" % self._layer_id
    initial = tf.constant(0.1, shape=[N_NEURONS])#\n" % self._n_neurons
    b = tf.Variable(initial, name='bias-22')#\n" % self._layer_id
    flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)
    node = tf.matmul(flat_node, W)    
    node = node + b
    Y2 = tf.sigmoid(node)
    '''
    X = {
        '1': {'Y': Y1},
        '2': {'Y': Y2}        
    }

    tr = TrainReinforceCodeGenerator(online_network_id='1', target_network_id='2',
                                     layer_pairs=[LayerPair('11', '21')],                        
                                     history_length=SEQ_SIZE)
    code = tr.get_code()

    glob_ = {'tf': tf, 'np': np, 'state_tensor': state_tensor, 'env': env, 'api': api}    
    loc_ = {'X': X}
    try:
        exec(code, glob_, loc_)
    except:
        for i, l in enumerate(code.split('\n'), 1):
            print(i, l)
        raise
        



    """ # BELOW IS A WORKING TEST CASE
    #import pdb; pdb.set_trace()

    
    import tensorflow as tf
    import numpy as np
    import gym

    np.random.seed(456)
    tf.set_random_seed(456)
    
    #env = gym.make('Breakout-v0')
    from unittest import mock
    api = mock.Mock()    
    env = DummyEnv()
    
    sample = env.reset()
    SEQ_SIZE = 2
    state_window_shape = (None, SEQ_SIZE, ) + sample.shape # [None, 4, 210, 160, 3]
    #print(state_window_shape)
    #raise SystemExit
    state_tensor = tf.placeholder(tf.float32, shape=state_window_shape, name='state_tensor')

    #import pdb; pdb.set_trace()

    # Online Network 
    N_NEURONS = 4 # n actions
    X = {'Y':  state_tensor}
    input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]
    shape = [input_size, N_NEURONS]
    initial = tf.truncated_normal(shape, stddev=0.1)
    W = tf.Variable(initial, name='weights-11')#\n" % self._layer_id
    initial = tf.constant(0.1, shape=[N_NEURONS])#\n" % self._n_neurons
    b = tf.Variable(initial, name='bias-11')#\n" % self._layer_id
    flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)
    node = tf.matmul(flat_node, W)    
    node = node + b
    Y1 = node

    '''
    X = {'Y':  Y1}
    input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]
    shape = [input_size, N_NEURONS]
    initial = tf.truncated_normal(shape, stddev=0.1)
    W = tf.Variable(initial, name='weights-12')#\n" % self._layer_id
    initial = tf.constant(0.1, shape=[N_NEURONS])#\n" % self._n_neurons
    b = tf.Variable(initial, name='bias-12')#\n" % self._layer_id
    flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)
    node = tf.matmul(flat_node, W)    
    node = node + b
    Y1 = tf.sigmoid(node)
    '''
    
    
    # Target Network 
    N_NEURONS = 4 # n actions
    X = {'Y':  state_tensor}
    input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]
    shape = [input_size, N_NEURONS]
    initial = tf.truncated_normal(shape, stddev=0.1)
    W = tf.Variable(initial, name='weights-21')#\n" % self._layer_id
    initial = tf.constant(0.1, shape=[N_NEURONS])#\n" % self._n_neurons
    b = tf.Variable(initial, name='bias-21')#\n" % self._layer_id
    flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)
    node = tf.matmul(flat_node, W)    
    node = node + b
    Y2 = node
    '''
    X = {'Y':  Y2}
    input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]
    shape = [input_size, N_NEURONS]
    initial = tf.truncated_normal(shape, stddev=0.1)
    W = tf.Variable(initial, name='weights-22')#\n" % self._layer_id
    initial = tf.constant(0.1, shape=[N_NEURONS])#\n" % self._n_neurons
    b = tf.Variable(initial, name='bias-22')#\n" % self._layer_id
    flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)
    node = tf.matmul(flat_node, W)    
    node = node + b
    Y2 = tf.sigmoid(node)
    '''
    X = {
        '1': {'Y': Y1},
        '2': {'Y': Y2}        
    }

    tr = TrainReinforceCodeGenerator(online_network_id='1', target_network_id='2',
                                     layer_pairs=[LayerPair('11', '21')],                        
                                     history_length=SEQ_SIZE)
    code = tr.get_code()

    glob_ = {'tf': tf, 'np': np, 'state_tensor': state_tensor, 'env': env, 'api': api}    
    loc_ = {'X': X}
    try:
        exec(code, glob_, loc_)
    except:
        for i, l in enumerate(code.split('\n'), 1):
            print(i, l)
        raise
        
    
        
    
    """
