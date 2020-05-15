import tensorflow as tf
import numpy as np
import dill
import os
import pickle
import zmq
import sys
import json
import time
import zlib
from queue import Queue
import logging
import threading
from typing import Dict, Any, List, Tuple, Generator
from flask import Flask, jsonify
from tensorflow.python.training.tracking.base import Trackable
import flask

from perceptilabs.core_new.utils import Picklable, YieldLevel
from perceptilabs.core_new.communication.status import *
from perceptilabs.core_new.layers import *
from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP, REPLICATED_PROPERTIES_TABLE
from perceptilabs.core_new.graph import Graph
from perceptilabs.core_new.graph.builder import GraphBuilder, SnapshotBuilder
from perceptilabs.core_new.api.mapping import MapServer, ByteMap
from perceptilabs.core_new.serialization import can_serialize, serialize


log = logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)
class ZmqHandler(logging.Handler):
    def emit(self, record):
        body = pickle.dumps(record.msg)
        message_queue.put((b'log_message', body))
global graph, status, t_start, socket
graph = None
socket = None
status = STATUS_INITIALIZING
t_start = None


class DataData_Data_1(DataLayer):
    """Class responsible for loading data from files (e.g., numpy, csv, etc)."""    
    def __init__(self):
        self._variables = {}
        columns = {}
        trn_sz_tot, val_sz_tot, tst_sz_tot = 0, 0, 0        
        trn_gens_args_DataData_Data_1, val_gens_args_DataData_Data_1, tst_gens_args_DataData_Data_1 = [], [], []        

        

        columns_DataData_Data_1_0 = None
    
        global matrix_DataData_Data_1_0
        matrix_DataData_Data_1_0 = np.load("C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Data/mnist_split/mnist_input.npy").astype(np.float32)
        size_DataData_Data_1_0 = len(matrix_DataData_Data_1_0)

        def generator_DataData_Data_1_0(idx_lo, idx_hi):
            global matrix_DataData_Data_1_0
            yield from matrix_DataData_Data_1_0[idx_lo:idx_hi].squeeze()


        if columns_DataData_Data_1_0 is not None:
            columns["DataData_Data_1_0"] = columns_DataData_Data_1_0

        trn_sz = int(round(0.01*70*size_DataData_Data_1_0))
        val_sz = int(round(0.01*20*size_DataData_Data_1_0))
        tst_sz = int(size_DataData_Data_1_0 - trn_sz - val_sz)

        trn_sz_tot += trn_sz
        val_sz_tot += val_sz
        tst_sz_tot += tst_sz
        
        trn_gens_args_DataData_Data_1.append((generator_DataData_Data_1_0, 0, trn_sz))
        val_gens_args_DataData_Data_1.append((generator_DataData_Data_1_0, trn_sz, trn_sz+val_sz))
        tst_gens_args_DataData_Data_1.append((generator_DataData_Data_1_0, trn_sz+val_sz, trn_sz+val_sz+tst_sz))
                    
        self._trn_gens_args = trn_gens_args_DataData_Data_1
        self._val_gens_args = val_gens_args_DataData_Data_1                                        
        self._tst_gens_args = tst_gens_args_DataData_Data_1
                    
        self._trn_sz_tot = trn_sz_tot
        self._val_sz_tot = val_sz_tot
        self._tst_sz_tot = tst_sz_tot
                    
        self._variables = {k: v for k, v in locals().items() if can_serialize(v)}

    @property
    def variables(self) -> Dict[str, Picklable]:
        """Returns any variables that the layer should make available and that can be pickled."""
        return self._variables

    @property
    def sample(self) -> np.ndarray:
        """Returns a single data sample"""                    
        sample = next(self.make_generator_training())
        return sample

    @property
    def size_training(self) -> int:
        """Returns the size of the training dataset"""                    
        return self._trn_sz_tot

    @property
    def size_validation(self) -> int:
        """Returns the size of the validation dataset"""
        return self._val_sz_tot

    @property
    def size_testing(self) -> int:
        """Returns the size of the testing dataset"""                    
        return self._tst_sz_tot
                    
    def make_generator_training(self) -> Generator[np.ndarray, None, None]:
        """Returns a generator yielding single samples of training data."""                                        
        def gen():
            for fn, lo, hi in self._trn_gens_args:
                for x in fn(lo, hi):
                    self._output = x
                    yield x
        return gen()
        
    def make_generator_validation(self) -> Generator[np.ndarray, None, None]:
        """Returns a generator yielding single samples of validation data."""                    
        def gen():
            for fn, lo, hi in self._val_gens_args:
                for x in fn(lo, hi):
                    self._output = x
                    yield x
        return gen()

    def make_generator_testing(self) -> Generator[np.ndarray, None, None]:
        """Returns a generator yielding single samples of testing data."""                            
        def gen():
            for fn, lo, hi in self._tst_gens_args:
                for x in fn(lo, hi):
                    self._output = x
                    yield x
        return gen()

class ProcessReshape_Reshape_1(Tf1xLayer):
    def __call__(self, x: tf.Tensor) -> tf.Tensor:
        """ Takes a tensor as input and reshapes it."""
        y = tf.reshape(x, [-1] + [28, 28, 1])
        y = tf.transpose(y, perm=[0] + [i+1 for i in [0, 1, 2]])
        return y

    @property
    def variables(self) -> Dict[str, Picklable]:
        """Any variables belonging to this layer that should be rendered in the frontend.
        
        Returns:
            A dictionary with tensor names for keys and picklable for values.
        """
        return {}

    @property
    def trainable_variables(self) -> Dict[str, tf.Tensor]:
        """Any trainable variables belonging to this layer that should be updated during backpropagation. Their gradients will also be rendered in the frontend.
        
        Returns:
            A dictionary with tensor names for keys and tensors for values.
        """
        return {}

    @property
    def weights(self) -> Dict[str, tf.Tensor]:
        """Any weight tensors belonging to this layer that should be rendered in the frontend.

        Return:
            A dictionary with tensor names for keys and tensors for values.
        """        
        return {}

    @property
    def biases(self) -> Dict[str, tf.Tensor]:
        """Any weight tensors belonging to this layer that should be rendered in the frontend.

        Return:
            A dictionary with tensor names for keys and tensors for values.
        """        
        return {}        

class DeepLearningConv_Convolution_1(Tf1xLayer):
    def __init__(self):
        self._scope = 'DeepLearningConv_Convolution_1'        
        # TODO: implement support for 1d and 3d conv, dropout, funcs, pooling, etc
        self._patch_size = 3
        self._feature_maps = 8
        self._padding = 'SAME'
        self._stride = 2
        
        self._variables = {}
        
    def __call__(self, x):
        """ Takes a tensor as input and feeds it forward through a convolutional layer, returning a newtensor."""                
        shape = [
            self._patch_size,
            self._patch_size,
            x.get_shape().as_list()[-1],
            self._feature_maps
        ]

        with tf.compat.v1.variable_scope(self._scope, reuse=tf.compat.v1.AUTO_REUSE):
            initial = tf.random.truncated_normal(
                shape,
                stddev=np.sqrt(2/(self._patch_size)**2 + self._feature_maps)
            )
            W = tf.compat.v1.get_variable('W', initializer=initial)
            
            initial = tf.constant(0.1, shape=[self._feature_maps])
            b = tf.compat.v1.get_variable('b', initializer=initial)
            y = tf.nn.conv2d(x, W, strides=[1, self._stride, self._stride, 1], padding=self._padding) + b
            y = tf.compat.v1.sigmoid(y)
            
        self._variables = {k: v for k, v in locals().items() if can_serialize(v)}
        return y

    @property
    def variables(self):
        """Any variables belonging to this layer that should be rendered in the frontend.
        
        Returns:
            A dictionary with tensor names for keys and picklable for values.
        """
        return self._variables.copy()

    @property
    def trainable_variables(self):
        """Any trainable variables belonging to this layer that should be updated during backpropagation. Their gradients will also be rendered in the frontend.
        
        Returns:
            A dictionary with tensor names for keys and tensors for values.
        """
        variables = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=self._scope)
        variables = {v.name: v for v in variables}
        return variables        

    @property
    def weights(self):
        """Any weight tensors belonging to this layer that should be rendered in the frontend.

        Return:
            A dictionary with tensor names for keys and tensors for values.
        """        
        with tf.compat.v1.variable_scope(self._scope, reuse=tf.compat.v1.AUTO_REUSE):
            w = tf.compat.v1.get_variable('W')
            return {w.name: w}

    @property
    def biases(self):
        """Any weight tensors belonging to this layer that should be rendered in the frontend.

        Return:
            A dictionary with tensor names for keys and tensors for values.
        """        
        with tf.compat.v1.variable_scope(self._scope, reuse=tf.compat.v1.AUTO_REUSE):
            b = tf.compat.v1.get_variable('b')
            return {b.name: b}

class DataData_Data_2(DataLayer):
    """Class responsible for loading data from files (e.g., numpy, csv, etc)."""    
    def __init__(self):
        self._variables = {}
        columns = {}
        trn_sz_tot, val_sz_tot, tst_sz_tot = 0, 0, 0        
        trn_gens_args_DataData_Data_2, val_gens_args_DataData_Data_2, tst_gens_args_DataData_Data_2 = [], [], []        

        

        columns_DataData_Data_2_0 = None
    
        global matrix_DataData_Data_2_0
        matrix_DataData_Data_2_0 = np.load("C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Data/mnist_split/mnist_labels.npy").astype(np.float32)
        size_DataData_Data_2_0 = len(matrix_DataData_Data_2_0)

        def generator_DataData_Data_2_0(idx_lo, idx_hi):
            global matrix_DataData_Data_2_0
            yield from matrix_DataData_Data_2_0[idx_lo:idx_hi].squeeze()


        if columns_DataData_Data_2_0 is not None:
            columns["DataData_Data_2_0"] = columns_DataData_Data_2_0

        trn_sz = int(round(0.01*70*size_DataData_Data_2_0))
        val_sz = int(round(0.01*20*size_DataData_Data_2_0))
        tst_sz = int(size_DataData_Data_2_0 - trn_sz - val_sz)

        trn_sz_tot += trn_sz
        val_sz_tot += val_sz
        tst_sz_tot += tst_sz
        
        trn_gens_args_DataData_Data_2.append((generator_DataData_Data_2_0, 0, trn_sz))
        val_gens_args_DataData_Data_2.append((generator_DataData_Data_2_0, trn_sz, trn_sz+val_sz))
        tst_gens_args_DataData_Data_2.append((generator_DataData_Data_2_0, trn_sz+val_sz, trn_sz+val_sz+tst_sz))
                    
        self._trn_gens_args = trn_gens_args_DataData_Data_2
        self._val_gens_args = val_gens_args_DataData_Data_2                                        
        self._tst_gens_args = tst_gens_args_DataData_Data_2
                    
        self._trn_sz_tot = trn_sz_tot
        self._val_sz_tot = val_sz_tot
        self._tst_sz_tot = tst_sz_tot
                    
        self._variables = {k: v for k, v in locals().items() if can_serialize(v)}

    @property
    def variables(self) -> Dict[str, Picklable]:
        """Returns any variables that the layer should make available and that can be pickled."""
        return self._variables

    @property
    def sample(self) -> np.ndarray:
        """Returns a single data sample"""                    
        sample = next(self.make_generator_training())
        return sample

    @property
    def size_training(self) -> int:
        """Returns the size of the training dataset"""                    
        return self._trn_sz_tot

    @property
    def size_validation(self) -> int:
        """Returns the size of the validation dataset"""
        return self._val_sz_tot

    @property
    def size_testing(self) -> int:
        """Returns the size of the testing dataset"""                    
        return self._tst_sz_tot
                    
    def make_generator_training(self) -> Generator[np.ndarray, None, None]:
        """Returns a generator yielding single samples of training data."""                                        
        def gen():
            for fn, lo, hi in self._trn_gens_args:
                for x in fn(lo, hi):
                    self._output = x
                    yield x
        return gen()
        
    def make_generator_validation(self) -> Generator[np.ndarray, None, None]:
        """Returns a generator yielding single samples of validation data."""                    
        def gen():
            for fn, lo, hi in self._val_gens_args:
                for x in fn(lo, hi):
                    self._output = x
                    yield x
        return gen()

    def make_generator_testing(self) -> Generator[np.ndarray, None, None]:
        """Returns a generator yielding single samples of testing data."""                            
        def gen():
            for fn, lo, hi in self._tst_gens_args:
                for x in fn(lo, hi):
                    self._output = x
                    yield x
        return gen()

class DeepLearningFC_Fully_Connected_1(Tf1xLayer):
    def __init__(self):
        self._scope = 'DeepLearningFC_Fully_Connected_1'
        self._n_neurons = 10
        self._variables = {}
        
    def __call__(self, x: tf.Tensor):
        """ Takes a tensor as input and feeds it forward through a layer of neurons, returning a newtensor."""        
        n_neurons = 10
        n_inputs = np.prod(x.get_shape().as_list()[1:], dtype=np.int32)

        with tf.compat.v1.variable_scope(self._scope, reuse=tf.compat.v1.AUTO_REUSE):        
            initial = tf.random.truncated_normal((n_inputs, self._n_neurons), stddev=0.1)
            W = tf.compat.v1.get_variable('W', initializer=initial)
            
            initial = tf.constant(0.1, shape=[self._n_neurons])
            b = tf.compat.v1.get_variable('b', initializer=initial)
            flat_node = tf.cast(tf.reshape(x, [-1, n_inputs]), dtype=tf.float32)
            y = tf.matmul(flat_node, W) + b

            y = tf.compat.v1.sigmoid(y)
            
        self._variables = {k: v for k, v in locals().items() if can_serialize(v)}            
        return y

    @property
    def variables(self):
        """Any variables belonging to this layer that should be rendered in the frontend.
        
        Returns:
            A dictionary with tensor names for keys and picklable for values.
        """
        return self._variables.copy()

    @property
    def trainable_variables(self):
        """Any trainable variables belonging to this layer that should be updated during backpropagation. Their gradients will also be rendered in the frontend.
        
        Returns:
            A dictionary with tensor names for keys and tensors for values.
        """
        variables = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=self._scope)
        variables = {v.name: v for v in variables}
        return variables

    @property
    def weights(self):
        """Any weight tensors belonging to this layer that should be rendered in the frontend.

        Return:
            A dictionary with tensor names for keys and tensors for values.
        """        
        with tf.compat.v1.variable_scope(self._scope, reuse=tf.compat.v1.AUTO_REUSE):
            w = tf.compat.v1.get_variable('W')
            return {w.name: w}

    @property
    def biases(self):
        """Any weight tensors belonging to this layer that should be rendered in the frontend.

        Return:
            A dictionary with tensor names for keys and tensors for values.
        """        
        with tf.compat.v1.variable_scope(self._scope, reuse=tf.compat.v1.AUTO_REUSE):
            b = tf.compat.v1.get_variable('b')
            return {b.name: b}    

class ProcessOneHot_OneHot_1(Tf1xLayer):
    def __call__(self, x):
        y = tf.one_hot(tf.cast(x, dtype=tf.int32), 10)        
        return y

    @property
    def variables(self) -> Dict[str, Picklable]:
        """Any variables belonging to this layer that should be rendered in the frontend.
        
        Returns:
            A dictionary with tensor names for keys and picklable for values.
        """
        return {}

    @property
    def trainable_variables(self) -> Dict[str, tf.Tensor]:
        """Any trainable variables belonging to this layer that should be updated during backpropagation. Their gradients will also be rendered in the frontend.
        
        Returns:
            A dictionary with tensor names for keys and tensors for values.
        """
        return {}

    @property
    def weights(self) -> Dict[str, tf.Tensor]:
        """Any weight tensors belonging to this layer that should be rendered in the frontend.

        Return:
            A dictionary with tensor names for keys and tensors for values.
        """        
        return {}

    @property    
    def biases(self) -> Dict[str, tf.Tensor]:
        """Any weight tensors belonging to this layer that should be rendered in the frontend.

        Return:
            A dictionary with tensor names for keys and tensors for values.
        """        
        return {}    

class TrainNormal_Normal_1(ClassificationLayer):
    def __init__(self):
        self._n_epochs = 10
        self._batch_size = 10 # TODO: ?

        self._stopped = False
        self._paused = False
        self._headless = False
        self._status = 'created'
        
        self._loss_training = 0.0
        self._loss_validation = 0.0
        self._loss_testing = 0.0      

        self._accuracy_training = 0.0
        self._accuracy_validation = 0.0
        self._accuracy_testing = 0.0      
        
        self._variables = {}
        self._layer_outputs = {}
        self._layer_weights = {}
        self._layer_biases = {}        
        self._layer_gradients = {}

        self._training_iteration = 0
        self._validation_iteration = 0
        self._testing_iteration = 0

        self._trn_sz_tot = 0
        self._val_sz_tot = 0
        self._tst_sz_tot = 0

        self._checkpoint = None
        
    def run(self, graph: Graph):
        """Called as the main entry point for training. Responsible for training the model.

        Args:
            graph: A PerceptiLabs Graph object containing references to all layers objects included in the model produced by this training layer.
        """   
        self._status = 'initializing'

        output_layer_id = '_Fully_Connected_1'
        target_layer_id = '_OneHot_1'
        input_data_nodes = graph.get_direct_data_nodes(output_layer_id)
        label_data_nodes = graph.get_direct_data_nodes(target_layer_id)

        assert len(input_data_nodes) == 1
        assert len(label_data_nodes) == 1
        input_data_node = input_data_nodes[0]
        label_data_node = label_data_nodes[0]

        self._trn_sz_tot = input_data_node.layer.size_training
        self._val_sz_tot = input_data_node.layer.size_validation
        self._tst_sz_tot = input_data_node.layer.size_testing

        # Make training set
        dataset_trn = tf.data.Dataset.zip((
            tf.data.Dataset.from_generator(
                input_data_node.layer_instance.make_generator_training,
                output_shapes=input_data_node.layer_instance.sample.shape,
                output_types=np.float32                
            ),
            tf.data.Dataset.from_generator(
                label_data_node.layer_instance.make_generator_training,
                output_shapes=label_data_node.layer_instance.sample.shape,
                output_types=np.float32
            )
        ))

        # Make validation set
        dataset_val = tf.data.Dataset.zip((
            tf.data.Dataset.from_generator(
                input_data_node.layer_instance.make_generator_validation,
                output_shapes=input_data_node.layer_instance.sample.shape,
                output_types=np.float32                
            ),
            tf.data.Dataset.from_generator(
                label_data_node.layer_instance.make_generator_validation,
                output_shapes=label_data_node.layer_instance.sample.shape,
                output_types=np.float32
            )
        ))

        # Make testing set
        dataset_tst = tf.data.Dataset.zip((
            tf.data.Dataset.from_generator(
                input_data_node.layer_instance.make_generator_testing,
                output_shapes=input_data_node.layer_instance.sample.shape,
                output_types=np.float32                
            ),
            tf.data.Dataset.from_generator(
                label_data_node.layer_instance.make_generator_testing,
                output_shapes=label_data_node.layer_instance.sample.shape,
                output_types=np.float32
            )
        ))

        dataset_trn = dataset_trn.batch(self._batch_size)
        dataset_val = dataset_val.batch(self._batch_size)
        dataset_tst = dataset_tst.batch(1)                

        # Make initializers
        iterator = tf.data.Iterator.from_structure(dataset_trn.output_types, dataset_trn.output_shapes)
        trn_init = iterator.make_initializer(dataset_trn)
        val_init = iterator.make_initializer(dataset_val)
        tst_init = iterator.make_initializer(dataset_tst)        
        input_tensor, label_tensor = iterator.get_next()

        # Build the TensorFlow graph # TODO: perhaps this part can be delegated to the graph?

        def build_graph(input_tensor, label_tensor):
            layer_output_tensors = {
                input_data_node.layer_id: input_tensor,
                label_data_node.layer_id: label_tensor
            }

            for node in graph.inner_nodes:
                args = []
                for input_node in graph.get_input_nodes(node):
                    args.append(layer_output_tensors[input_node.layer_id])
                    y = node.layer_instance(*args)
                layer_output_tensors[node.layer_id] = y


            return layer_output_tensors

        layer_output_tensors = build_graph(input_tensor, label_tensor)
        output_tensor = layer_output_tensors[output_layer_id]
        target_tensor = layer_output_tensors[target_layer_id]

        # Create an exportable version of the TensorFlow graph
        self._input_tensor_export = tf.placeholder(shape=dataset_trn.output_shapes[0], dtype=dataset_trn.output_types[0])
        self._output_tensor_export = build_graph(
            self._input_tensor_export,
            tf.placeholder(shape=dataset_trn.output_shapes[1], dtype=dataset_trn.output_types[1])
        )[output_layer_id]

        loss_tensor = tf.reduce_mean(tf.square(output_tensor - target_tensor))
        correct_predictions = tf.equal(tf.argmax(output_tensor, -1), tf.argmax(target_tensor, -1))
        accuracy_tensor = tf.reduce_mean(tf.cast(correct_predictions, tf.float32))

        global_step = None

        optimizer = tf.train.AdamOptimizer(learning_rate=0.001, beta1=0.9, beta2=0.999)

        layer_weight_tensors = {}
        layer_bias_tensors = {}        
        layer_gradient_tensors = {}
        for node in graph.inner_nodes:
            if not isinstance(node.layer, Tf1xLayer): # In case of pure custom layers...
                continue
            
            layer_weight_tensors[node.layer_id] = node.layer.weights
            layer_bias_tensors[node.layer_id] = node.layer.biases            
            
            if len(node.layer.trainable_variables) > 0:
                gradients = {}
                for name, tensor in node.layer.trainable_variables.items():
                    grad_tensor = tf.gradients(loss_tensor, tensor)
                    if any(x is None for x in grad_tensor):
                        grad_tensor = tf.constant(0)
                    gradients[name] = grad_tensor
                layer_gradient_tensors[node.layer_id] = gradients
                # self._internal_layer_gradients[node.layer_id] = {name: [] for name in node.layer.trainable_variables.keys()} # Initialize
                # self._layer_gradients = self._internal_layer_gradients.copy()

        trainable_vars = tf.trainable_variables() # TODO: safer to get from nodes. Especially with split graph in mind.
        grads = tf.gradients(loss_tensor, trainable_vars)
        update_weights = optimizer.apply_gradients(zip(grads, trainable_vars), global_step=global_step)        

        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        sess = tf.Session(config=config)
        self._sess = sess

        trackable_variables = {}
        trackable_variables.update({x.name: x for x in tf.trainable_variables() if isinstance(x, Trackable)})
        trackable_variables.update({k: v for k, v in locals().items() if isinstance(v, Trackable) and not isinstance(v, tf.python.data.ops.iterator_ops.Iterator)}) # TODO: Iterators based on 'stateful functions' cannot be serialized.
        self._checkpoint = tf.train.Checkpoint(**trackable_variables)
        sess.run(tf.global_variables_initializer())
        
                    
        
        def train_step():
            if not self._headless:
                _, self._loss_training, self._accuracy_training, \
                    self._layer_outputs, self._layer_weights, self._layer_biases, \
                    self._layer_gradients \
                    = sess.run([
                        update_weights, loss_tensor, accuracy_tensor,
                        layer_output_tensors, layer_weight_tensors, layer_bias_tensors, layer_gradient_tensors
                    ])
            else:
                _, self._loss_training, self._accuracy_training, \
                    = sess.run([
                        update_weights, loss_tensor, accuracy_tensor
                    ])
            
        def validation_step():
            if not self._headless:
                self._loss_validation, self._accuracy_validation, \
                    self._layer_outputs, self._layer_weights, self._layer_biases, \
                    self._layer_gradients \
                    = sess.run([
                        loss_tensor, accuracy_tensor,
                        layer_output_tensors, layer_weight_tensors, layer_bias_tensors, layer_gradient_tensors
                    ])
            else:
                self._loss_validation, self._accuracy_validation, \
                    = sess.run([
                        loss_tensor, accuracy_tensor
                    ])

            
        def test_step():
            self._loss_testing, self._accuracy_testing, \
                self._layer_outputs, self._layer_weights, self._layer_gradients \
                = sess.run([
                    loss_tensor, accuracy_tensor,
                    layer_output_tensors, layer_weight_tensors, layer_gradient_tensors
                ])
            #accuracy_list.append(acc)
            #loss_list.append(loss)

        self._variables = {k: v for k, v in locals().items() if can_serialize(v)}

        log.info("Entering training loop")

        # Training loop
        self._epoch = 0
        while self._epoch < self._n_epochs and not self._stopped:
            t0 = time.perf_counter()
            self._training_iteration = 0
            self._validation_iteration = 0
            self._status = 'training'
            sess.run(trn_init)            
            try:
                while not self._stopped:
                    train_step()
                    yield YieldLevel.SNAPSHOT
                    self._training_iteration += 1
            except tf.errors.OutOfRangeError:
                pass

            self._status = 'validation'
            sess.run(val_init)            
            try:
                while not self._stopped:
                    validation_step()
                    yield YieldLevel.SNAPSHOT                    
                    self._validation_iteration += 1
            except tf.errors.OutOfRangeError:
                pass
            log.info(
                f"Finished epoch {self._epoch+1}/{self._n_epochs} - "
                f"loss training, validation: {self.loss_training:.6f}, {self.loss_validation:.6f} - "
                f"acc. training, validation: {self.accuracy_training:.6f}, {self.accuracy_validation:.6f}"
            )
            log.info(f"Epoch duration: {round(time.perf_counter() - t0, 3)} s")            
            self._epoch += 1

        self._variables = {k: v for k, v in locals().items() if can_serialize(v)}            
        yield YieldLevel.DEFAULT            
        
        # Test loop
        self._testing_iteration = 0
        self._status = 'testing'
        sess.run(tst_init)                                
        try:
            while not self._stopped:
                test_step()
                yield YieldLevel.SNAPSHOT
                self._testing_iteration += 1
        except tf.errors.OutOfRangeError:
            pass

        self._status = 'finished'
        self._variables = {k: v for k, v in locals().items() if can_serialize(v)}
        yield YieldLevel.DEFAULT

                

    def on_export(self, path: str, mode: str) -> None:
        """Called when the export or save button is clicked in the frontend.
        It is up to the implementing layer to save the model to disk.
        
        Args:
            path: the directory where the exported model will be stored.
            mode: how to export the model. Made available to frontend via 'export_modes' property."""

        log.debug(f"Export called. Project path = {path}, mode = {mode}")
        pb_path = os.path.join(path, '1')
        
        # Export non-compressed model
        if mode in ['TFModel', 'TFModel+checkpoint']:
            tf.compat.v1.saved_model.simple_save(self._sess, pb_path, inputs={'input': self._input_tensor_export}, outputs={'output': self._output_tensor_export})

        # Export compressed model
        if mode in ['TFLite', 'TFLite+checkpoint']:
            converter = tf.lite.TFLiteConverter.from_session(self._sess, [self._input_tensor_export], [self._output_tensor_export])
            converter.post_training_quantize = True
            tflite_model = converter.convert()
            open(pb_path, "wb").write(tflite_model)

        # Export checkpoint
        if mode in ['TFModel+checkpoint', 'TFLite+checkpoint']:
            self._checkpoint.save(file_prefix=os.path.join(path, 'model.ckpt'), session=self._sess)
                
    def on_stop(self) -> None:
        """Called when the save model button is clicked in the frontend. 
        It is up to the implementing layer to save the model to disk."""
        self._stopped = True

    def on_headless_activate(self) -> None:
        """"Called when the statistics shown in statistics window are not needed.
        Purose is to speed up the iteration speed significantly."""
        self._headless = True

        self._layer_outputs = {} 
        self._layer_weights = {}
        self._layer_biases = {}
        self._layer_gradients = {}

    def on_headless_deactivate(self) -> None:
        """"Called when the statistics shown in statistics window are needed.
        May slow down the iteration speed of the training."""
        import time
        log.info(f"Set to headless_off at time {time.time()}")
        self._headless = False

    @property
    def export_modes(self) -> List[str]:
        """Returns the possible modes of exporting a model."""        
        return [
            'TFModel',
            'TFLite'
            'TFModel+checkpoint',
            'TFLite+checkpoint',            
        ]
        
    @property
    def is_paused(self) -> None:
        """Returns true when the training is paused."""        
        return self._paused

    @property
    def batch_size(self):
        """ Size of the current training batch """        
        return self._batch_size

    @property
    def status(self):
        """Called when the pause button is clicked in the frontend. It is up to the implementing layer to pause its execution."""        
        return self._status
    
    @property
    def epoch(self):
        """The current epoch"""        
        return self._epoch

    @property
    def variables(self):
        """Any variables belonging to this layer that should be rendered in the frontend.
        
        Returns:
            A dictionary with tensor names for keys and picklable for values.
        """
        return self._variables.copy()        

    @property
    def sample(self) -> np.ndarray:
        """Returns a single data sample"""        
        return np.empty(())

    @property
    def size_training(self) -> int:
        """Returns the size of the training dataset"""                                    
        return self._trn_sz_tot

    @property
    def size_validation(self) -> int:
        """Returns the size of the validation dataset"""                                            
        return self._val_sz_tot

    @property
    def size_testing(self) -> int:
        """Returns the size of the testing dataset"""
        return self._tst_sz_tot

    def make_generator_training(self) -> Generator[np.ndarray, None, None]:
        """Returns a generator yielding single samples of training data. In the case of a training layer, this typically yields the model output."""        
        # Simply call sess.run on the output & target tensors :)  #TODO: how to make generators generic? We have two datasets here, but not all datasets will be labeled. Distinguish between supervised/unsupervised data layers and instead REQUIRE pairs of data layers for supervised?
        yield from []
        
    def make_generator_validation(self) -> Generator[np.ndarray, None, None]:
        """Returns a generator yielding single samples of validation data. In the case of a training layer, this typically yields the model output."""                
        yield from []
        
    def make_generator_testing(self) -> Generator[np.ndarray, None, None]:
        """Returns a generator yielding single samples of testing data. In the case of a training layer, this typically yields the model output."""                        
        yield from []

    @property
    def accuracy_training(self) -> float:
        """Returns the current accuracy of the training phase"""        
        return self._accuracy_training
    
    @property
    def accuracy_validation(self) -> float:
        """Returns the current accuracy of the validation phase"""                
        return self._accuracy_validation

    @property
    def accuracy_testing(self) -> float:
        """Returns the current accuracy of the testing phase"""                        
        return self._accuracy_testing

    @property
    def loss_training(self) -> float:
        """Returns the current loss of the training phase"""                
        return self._loss_training        

    @property
    def loss_validation(self) -> float:
        """Returns the current loss of the validation phase"""                        
        return self._loss_validation        

    @property
    def loss_testing(self) -> float:
        """Returns the current loss of the testing phase"""                
        return self._loss_testing

    @property
    def layer_weights(self) -> Dict[str, Dict[str, Picklable]]:
        """The weight values of each layer in the input Graph during the training.

        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain weight name and value pairs. The values must be picklable.
        """        
        return self._layer_weights

    @property
    def layer_biases(self) -> Dict[str, Dict[str, Picklable]]:
        """The bias values of each layer in the input Graph during the training.

        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain weight name and value pairs. The values must be picklable.
        """        
        return self._layer_biases
    
    @property
    def layer_gradients(self) -> Dict[str, Dict[str, Picklable]]:
        """The gradients with respect to the loss of all trainable variables of each layer in the input Graph.

        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain gradient name and value pairs. The values must be picklable.
        """        
        return self._layer_gradients
    
    @property
    def layer_outputs(self) -> Dict[str, Dict[str, Picklable]]:
        """The output values of each layer in the input Graph during the training (e.g., tf.Tensors evaluated for each iteration)

        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain variable name and value pairs. The values must be picklable.
        """
        return self._layer_outputs

    @property
    def training_iteration(self) -> int:
        """The current training iteration"""
        return self._training_iteration

    @property
    def validation_iteration(self) -> int:
        """The current validation iteration"""        
        return self._validation_iteration

    @property
    def testing_iteration(self) -> int:
        """The current testing iteration"""                
        return self._testing_iteration
    
    @property
    def progress(self) -> float:
        """A number indicating the overall progress of the training
        
        Returns:
            A floating point number between 0 and 1
        """        
        n_iterations_per_epoch = np.ceil(self.size_training / self.batch_size) + \
                                 np.ceil(self.size_validation / self.batch_size)
        n_iterations_total = self._n_epochs * n_iterations_per_epoch

        iteration = self.epoch * n_iterations_per_epoch + \
                    self.training_iteration + self.validation_iteration
        
        progress = min(iteration/(n_iterations_total - 1), 1.0) 
        return progress


LAYERS = {
    '_Data_1': DataData_Data_1(),
    '_Reshape_1': ProcessReshape_Reshape_1(),
    '_Convolution_1': DeepLearningConv_Convolution_1(),
    '_Data_2': DataData_Data_2(),
    '_Fully_Connected_1': DeepLearningFC_Fully_Connected_1(),
    '_OneHot_1': ProcessOneHot_OneHot_1(),
    '_Normal_1': TrainNormal_Normal_1(),
}

EDGES = {
    ('_Data_1', '_Reshape_1'),
    ('_Reshape_1', '_Convolution_1'),
    ('_Convolution_1', '_Fully_Connected_1'),
    ('_Data_2', '_OneHot_1'),
    ('_Fully_Connected_1', '_Normal_1'),
    ('_OneHot_1', '_Normal_1'),
}

global snapshots_produced
snapshots_produced = 0
snapshots = []
snapshot_lock = threading.Lock()

message_queue = Queue()
event_queue = Queue()

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

@app.route('/snapshot_count')
def endpoint_count():
    return str(len(snapshots))
@app.route('/snapshot')
def endpoint_snapshot():
    from flask import request
    index = int(request.args.get('index'))
    try:
        with snapshot_lock:
            pickled_snapshot = dill.dumps(snapshots[index])
        compressed_snapshot = zlib.compress(pickled_snapshot)
        hex_snapshot = compressed_snapshot.hex()
        return hex_snapshot
    except Exception as e:
         import boltons.iterutils
         non_picklable = boltons.iterutils.research(snapshots[index], query=lambda p, k, v: type(v) not in [list, dict, set, tuple] and not can_serialize(v))
         if non_picklable:
             print('not picklable:', non_picklable)
         raise
@app.route('/command', methods=['POST'])
def endpoint_event():
    from flask import request
    global status
    data = request.json
    event_queue.put(data)
    log.debug(f'Received event. Data: {str(data)}. Queue size = {event_queue.qsize()}')
    return jsonify(success=True)
@app.route('/')
def endpoint_index():
    global status, t_start, snapshots_produced
    result = {
        'status': status,
        'n_snapshots': snapshots_produced,
        'snapshot_count': snapshots_produced,
        'running_time': time.perf_counter() - t_start if t_start is not None else None
    }
    return jsonify(result)
snapshot_builder = SnapshotBuilder(
    BASE_TO_REPLICA_MAP, 
    REPLICATED_PROPERTIES_TABLE
)

def process_events(graph):
    global status
    while not event_queue.empty():
        event_data = event_queue.get()
        event_type = event_data['type']
        log.debug('Processing event: ' + str(event_type) + ' '+ str(event_data))
        
        if event_type == 'on_pause':
            if status == STATUS_RUNNING:
                status = STATUS_RUNNING_PAUSED
        elif event_type == 'on_resume':
            if status == STATUS_RUNNING_PAUSED:
                status = STATUS_RUNNING
        elif event_type == 'on_start':
            status = STATUS_STARTED
        elif event_type == 'on_stop':
            status = STATUS_STOPPED
            graph.active_training_node.layer.on_stop()
        elif event_type == 'on_headless_activate':
            graph.active_training_node.layer.on_headless_activate()
        elif event_type == 'on_headless_deactivate':
            graph.active_training_node.layer.on_headless_deactivate()
        elif event_type == 'on_export':
            graph.active_training_node.layer.on_export(event_data['path'], event_data['mode'])

def make_snapshot(graph):
    global snapshot_lock, snapshots, snapshots_produced
    snapshot = snapshot_builder.build(graph)
    snapshots_produced += 1
    body = serialize(snapshot)
    message_queue.put((b'snapshots', body))
    process_events(graph)

def make_snapshot_and_process_events(graph):
    make_snapshot(graph)
    process_events(graph)

def message_queue_worker():
    while True:
        if message_queue.empty():
            time.sleep(0.01)
        else:
            topic, body = message_queue.get()
            socket.send_multipart([topic, body])

def run_training():
    global status
    try:
        iterator = graph.training_nodes[0].layer_instance.run(graph)
        result = None
        sentinel = object()
        while result is not sentinel:
            result = next(iterator, sentinel)
            if result is YieldLevel.SNAPSHOT:
                make_snapshot(graph)
            if result is not sentinel:
                process_events(graph)
            while status == STATUS_RUNNING_PAUSED and result is not sentinel:
                process_events(graph)
                time.sleep(0.5)
        
    except Exception as e:
        import traceback
        tb_list = traceback.extract_tb(e.__traceback__)
        body = pickle.dumps((e, tb_list))
        message_queue.put((b'exception', body))
        raise

def get_graph():
    global graph
    graph_builder = GraphBuilder()
    graph = graph_builder.build(LAYERS, EDGES)
    return graph
def main(wait=False):
    print('Flask port: 5678')
    global graph, status, t_start, socket
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind('tcp://*:5679')
    log.addHandler(ZmqHandler())
    threading.Thread(target=app.run, kwargs={"port": "5678", "threaded": True}, daemon=True).start()
    threading.Thread(target=message_queue_worker, daemon=True).start()
    graph = get_graph()
    
    print(graph.training_nodes)
    graph.training_nodes[0].layer_instance.save_snapshot = make_snapshot_and_process_events
    graph.training_nodes[0].layer_instance.save_snapshot_and_process_events = make_snapshot_and_process_events
    graph.training_nodes[0].layer_instance.process_events = process_events
    status = STATUS_READY
    if wait:
        while status != STATUS_STARTED:
            process_events(graph)
            time.sleep(1.0)
        
        status = STATUS_RUNNING
        t_start = time.perf_counter()
        run_training()
        
        if status != STATUS_STOPPED:
            status = STATUS_IDLE
        while status != STATUS_STOPPED:
            process_events(graph)
            time.sleep(1.0)
    else:
        status = STATUS_RUNNING
        t_start = time.perf_counter()
        run_training()

    status = STATUS_DONE
    process_events(graph)
    log.debug(f'Terminating. Event queue size = {event_queue.qsize()}')


if __name__ == "__main__":
    wait = "--wait" in sys.argv
    main(wait)
