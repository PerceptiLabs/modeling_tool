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


class DataData_data_inputs(DataLayer):
    """Class responsible for loading data from files (e.g., numpy, csv, etc)."""    
    def __init__(self):
        self._variables = {}
        columns = {}
        trn_sz_tot, val_sz_tot, tst_sz_tot = 0, 0, 0        
        trn_gens_args_DataData_data_inputs, val_gens_args_DataData_data_inputs, tst_gens_args_DataData_data_inputs = [], [], []        

        

        columns_DataData_data_inputs_0 = None
    
        global matrix_DataData_data_inputs_0
        matrix_DataData_data_inputs_0 = np.load("C:/Users/Robert/AppData/Local/Temp/tmpqytsc7ls.npy").astype(np.float32)
        size_DataData_data_inputs_0 = len(matrix_DataData_data_inputs_0)

        def generator_DataData_data_inputs_0(idx_lo, idx_hi):
            global matrix_DataData_data_inputs_0
            yield from matrix_DataData_data_inputs_0[idx_lo:idx_hi].squeeze()


        if columns_DataData_data_inputs_0 is not None:
            columns["DataData_data_inputs_0"] = columns_DataData_data_inputs_0

        trn_sz = int(round(0.01*70*size_DataData_data_inputs_0))
        val_sz = int(round(0.01*20*size_DataData_data_inputs_0))
        tst_sz = int(size_DataData_data_inputs_0 - trn_sz - val_sz)

        trn_sz_tot += trn_sz
        val_sz_tot += val_sz
        tst_sz_tot += tst_sz
        
        trn_gens_args_DataData_data_inputs.append((generator_DataData_data_inputs_0, 0, trn_sz))
        val_gens_args_DataData_data_inputs.append((generator_DataData_data_inputs_0, trn_sz, trn_sz+val_sz))
        tst_gens_args_DataData_data_inputs.append((generator_DataData_data_inputs_0, trn_sz+val_sz, trn_sz+val_sz+tst_sz))
                    
        self._trn_gens_args = trn_gens_args_DataData_data_inputs
        self._val_gens_args = val_gens_args_DataData_data_inputs                                        
        self._tst_gens_args = tst_gens_args_DataData_data_inputs
                    
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

class DataData_data_labels(DataLayer):
    """Class responsible for loading data from files (e.g., numpy, csv, etc)."""    
    def __init__(self):
        self._variables = {}
        columns = {}
        trn_sz_tot, val_sz_tot, tst_sz_tot = 0, 0, 0        
        trn_gens_args_DataData_data_labels, val_gens_args_DataData_data_labels, tst_gens_args_DataData_data_labels = [], [], []        

        

        columns_DataData_data_labels_0 = None
    
        global matrix_DataData_data_labels_0
        matrix_DataData_data_labels_0 = np.load("C:/Users/Robert/AppData/Local/Temp/tmpv0nqf7sn.npy").astype(np.float32)
        size_DataData_data_labels_0 = len(matrix_DataData_data_labels_0)

        def generator_DataData_data_labels_0(idx_lo, idx_hi):
            global matrix_DataData_data_labels_0
            yield from matrix_DataData_data_labels_0[idx_lo:idx_hi].squeeze()


        if columns_DataData_data_labels_0 is not None:
            columns["DataData_data_labels_0"] = columns_DataData_data_labels_0

        trn_sz = int(round(0.01*70*size_DataData_data_labels_0))
        val_sz = int(round(0.01*20*size_DataData_data_labels_0))
        tst_sz = int(size_DataData_data_labels_0 - trn_sz - val_sz)

        trn_sz_tot += trn_sz
        val_sz_tot += val_sz
        tst_sz_tot += tst_sz
        
        trn_gens_args_DataData_data_labels.append((generator_DataData_data_labels_0, 0, trn_sz))
        val_gens_args_DataData_data_labels.append((generator_DataData_data_labels_0, trn_sz, trn_sz+val_sz))
        tst_gens_args_DataData_data_labels.append((generator_DataData_data_labels_0, trn_sz+val_sz, trn_sz+val_sz+tst_sz))
                    
        self._trn_gens_args = trn_gens_args_DataData_data_labels
        self._val_gens_args = val_gens_args_DataData_data_labels                                        
        self._tst_gens_args = tst_gens_args_DataData_data_labels
                    
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

class ProcessReshape_reshape(Tf1xLayer):
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

class ProcessOneHot_one_hot(Tf1xLayer):
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

class DeepLearningFC_fc(Tf1xLayer):
    def __init__(self):
        self._scope = 'DeepLearningFC_fc'
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

class TrainNormal_training(ClassificationLayer):
    def __init__(self):
        self._n_epochs = 200
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
        INCLUDE_KERAS_METRICS = False

        self_layer_name = 'TrainNormal_training' # this is passed as input
        output_layer_id = '_fc'
        target_layer_id = '_one_hot'
        input_data_nodes = graph.get_direct_data_nodes(output_layer_id)
        label_data_nodes = graph.get_direct_data_nodes(target_layer_id)

        assert len(input_data_nodes) == 1
        assert len(label_data_nodes) == 1
        input_data_node = input_data_nodes[0]
        label_data_node = label_data_nodes[0]

        self._trn_sz_tot = input_data_node.layer.size_training
        self._val_sz_tot = input_data_node.layer.size_validation
        self._tst_sz_tot = input_data_node.layer.size_testing

        # Set Devices and Distribution Strategy
        n_devices = 4
        config = tf.ConfigProto(device_count={"CPU": n_devices, "GPU": 0},
                               gpu_options={"allow_growth": True},
                               inter_op_parallelism_threads=n_devices,
                               intra_op_parallelism_threads=1)
        # config = tf.ConfigProto(gpu_options={"allow_growth": True}, log_device_placement=True, allow_soft_placement=True)

        sess = tf.Session(config=config)
        tf.keras.backend.set_session(sess) # since we use keras metrics
        self._sess = sess

        strategy = tf.distribute.MirroredStrategy(devices=[f'/CPU:{i}' for i in range(n_devices)]) # TODO: not needed under real circumstances, should default to all.

        BATCH_SIZE_PER_REPLICA = self._batch_size # TODO: should this be batch_size divided by n_devices or not?
        GLOBAL_BATCH_SIZE = BATCH_SIZE_PER_REPLICA * n_devices

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

        train_dataset = dataset_trn.batch(GLOBAL_BATCH_SIZE)
        validation_dataset = dataset_val.batch(GLOBAL_BATCH_SIZE)
        test_dataset = dataset_tst.batch(1) # Since the batch size for test is 1, it does not make sense to divide the batch over several replicas. Do testing as usual.

        # NOTE: A key difference for distributed: we have one _iterator_ per dataset, as opposed to one _initializer_ per dataset in the normal case.
        # This means that we have to create a different version of all metrics (accuracy, f1, auc, etc), the gradients and more importantly: 'all tensors'.

        with strategy.scope():
            train_iterator = strategy.make_dataset_iterator(train_dataset)
            validation_iterator = strategy.make_dataset_iterator(validation_dataset)

        test_iterator = tf.data.Iterator.from_structure(test_dataset.output_types, test_dataset.output_shapes)
        test_iterator_init = test_iterator.make_initializer(test_dataset)

        def create_model():
            # The tensors generated by distributed iterators are only accessible locally from each replica. Therefore,
            # each replica must create its own version of the model. This has the following two consequences:
            #
            #     * all tensorflow variables/operations must be executed on device, once per replica => the wrapped layers are further wrapped as a Model.
            #     * we must keep track of the created variables, so that the validation steps can reuse the trained variables => we use get_variable instead of tf.Variable, with a var-scope for each layer.
            #     * we will have several instances/copies of non-trainable/non-tensorflow variables. => Each layer wrapper tracks the number of times it's been created, or they would overwrite eachother.
            
            class Model:
                def __init__(self):
                    pass
                
                def __call__(self, x, y):
                    layer_output_tensors = {
                        input_data_node.layer_id: x,
                        label_data_node.layer_id: y
                    }

                    for node in graph.inner_nodes:
                        args = []
                        for input_node in graph.get_input_nodes(node):
                            args.append(layer_output_tensors[input_node.layer_id])
                        y = node.layer_instance(*args)
                        layer_output_tensors[node.layer_id] = y

                    return layer_output_tensors 
            
            return Model()

        with strategy.scope():

            if INCLUDE_KERAS_METRICS:
                # contrib.f1_score and metrics.auc do not work with distributed. 
                # note: f1_score seems to be deprecated in tf2.0, so it makes sense that they haven't imported it in tf 2.0
                # https://stackoverflow.com/questions/53620581/calculate-f1-score-using-tf-metrics-precision-recall-in-a-tf-estimator-setup
                #
                # Likewise, AUC does not work properly for distributed. Keras metrics seem to be the recommended approach.
                # This works out of the box for AUC, but not for F1 score (not implemented). Using definition and going via Recall and Precision instead.
                
                num_thresholds=200
                epsilon = 1e-7
                thresholds = [(i+0) * 1.0 / (num_thresholds - 1) for i in range(num_thresholds - 0)]
                #thresholds = [0.0] + thresholds + [1.0]
                
                recall_train = tf.keras.metrics.Recall(thresholds=thresholds)
                precision_train = tf.keras.metrics.Precision(thresholds=thresholds)
                
                r = recall_train.result()
                p = precision_train.result()
                
                f1_train = tf.reduce_max(tf.math.divide_no_nan(2*r*p, r+p)) # TODO: create custom metric instead? make PR at tf?
                auc_train = tf.keras.metrics.AUC(curve='ROC')
                auc_train_tensor = auc_train.result()
                
                recall_val = tf.keras.metrics.Recall(thresholds=thresholds)
                precision_val = tf.keras.metrics.Precision(thresholds=thresholds)
                
                r = recall_val.result()
                p = precision_val.result()
                
                f1_val = tf.reduce_max(tf.math.divide_no_nan(2*r*p, r+p)) # TODO: create custom metric instead? make PR at tf?    
                auc_val = tf.keras.metrics.AUC(curve='ROC')
                auc_val_tensor = auc_val.result()
                
                
            model = create_model()
            
            train_iterator_init = train_iterator.initialize()
            validation_iterator_init = validation_iterator.initialize()

            global_step = None

            optimizer = tf.compat.v1.train.GradientDescentOptimizer(learning_rate=0.05*n_devices)
            
            def train_step(inputs):
                x, y = inputs
                layer_output_tensors = model(x, y)
                output_tensor = layer_output_tensors[output_layer_id]
                target_tensor = layer_output_tensors[target_layer_id]

                loss_tensor = tf.reduce_sum(tf.square(output_tensor - target_tensor)) / GLOBAL_BATCH_SIZE
                correct_predictions = tf.equal(tf.argmax(output_tensor,-1), tf.argmax(target_tensor,-1))
                accuracy_tensor = tf.reduce_mean(tf.cast(correct_predictions, tf.float32))

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
                            if type(grad_tensor) is list and len(grad_tensor) == 1:
                                gradients[name] = grad_tensor[0]
                            else:
                                gradients[name] = grad_tensor
                        layer_gradient_tensors[node.layer_id] = gradients
                        self._layer_gradients[node.layer_id] = {name: [] for name in node.layer.trainable_variables.keys()} # Initialize

                trainable_vars = tf.trainable_variables()
                grads = tf.gradients(loss_tensor, trainable_vars)        
                update_weights = optimizer.apply_gradients(zip(grads, trainable_vars), global_step=global_step)

                if INCLUDE_KERAS_METRICS:
                    update_auc = auc_train.update_state(target_tensor, output_tensor)
                    update_recall = recall_train.update_state(target_tensor, output_tensor)
                    update_precision = precision_train.update_state(target_tensor, output_tensor)
                    
                    update_ops = [update_weights, update_auc, update_recall, update_precision]
                else:
                    update_ops = [update_weights]

                with tf.control_dependencies(update_ops):
                    def add_identity(x):
                        if isinstance(x, dict):
                            return {k: add_identity(v) for k, v in x.items()}
                        else:
                            return tf.identity(x)
                    
                    # Only tensors CREATED in this scope will be affected. Therefore, we pass them through the identity operation.
                    return add_identity(loss_tensor), add_identity(accuracy_tensor), add_identity(layer_output_tensors), add_identity(layer_weight_tensors), add_identity(layer_bias_tensors), add_identity(layer_gradient_tensors)

            def validation_step(inputs):
                x, y = inputs
                layer_output_tensors = model(x, y)
                output_tensor = layer_output_tensors[output_layer_id]
                target_tensor = layer_output_tensors[target_layer_id]

                loss_tensor = tf.reduce_sum(tf.square(output_tensor - target_tensor)) / GLOBAL_BATCH_SIZE
                correct_predictions = tf.equal(tf.argmax(output_tensor,-1), tf.argmax(target_tensor,-1))
                accuracy_tensor = tf.reduce_mean(tf.cast(correct_predictions, tf.float32))

                layer_weight_tensors = {}
                layer_bias_tensors = {}        
                layer_gradient_tensors = {}
                for node in graph.inner_nodes:
                    layer_weight_tensors[node.layer_id] = node.layer.weights
                    layer_bias_tensors[node.layer_id] = node.layer.biases            
                    
                    if len(node.layer.trainable_variables) > 0:
                        gradients = {}
                        for name, tensor in node.layer.trainable_variables.items():
                            grad_tensor = tf.gradients(loss_tensor, tensor)
                            if any(x is None for x in grad_tensor):
                                grad_tensor = tf.constant(0)
                            if type(grad_tensor) is list and len(grad_tensor) == 1:
                                gradients[name] = grad_tensor[0]
                            else:
                                gradients[name] = grad_tensor
                        layer_gradient_tensors[node.layer_id] = gradients
                        self._layer_gradients[node.layer_id] = {name: [] for name in node.layer.trainable_variables.keys()} # Initialize

                if INCLUDE_KERAS_METRICS:
                    update_auc = auc_train.update_state(target_tensor, output_tensor)
                    update_recall = recall_train.update_state(target_tensor, output_tensor)
                    update_precision = precision_train.update_state(target_tensor, output_tensor)
                    
                    update_ops = [update_auc, update_recall, update_precision]
                else:
                    update_ops = []

                with tf.control_dependencies(update_ops):
                    def add_identity(x):
                        if isinstance(x, dict):
                            return {k: add_identity(v) for k, v in x.items()}
                        else:
                            return tf.identity(x)
                    
                    return add_identity(loss_tensor), add_identity(accuracy_tensor), add_identity(layer_output_tensors), add_identity(layer_weight_tensors), add_identity(layer_bias_tensors), add_identity(layer_gradient_tensors)


            if n_devices > 1:
                def reduce_per_replica(nested_dict):
                    for variable, node in nested_dict.items():
                        if type(node) is dict:
                            nested_dict[variable] = reduce_per_replica(node)
                        else:
                            tensors = [node.get(device) for device in node.devices \
                                    if node.get(device) is not None]
                            nested_dict[variable] = tensors[0]
                    return nested_dict

                ##### Training statistics #####
                dist_loss_train, accuracy_train, \
                    layer_outputs_train, layer_weights_train, layer_biases_train, \
                    layer_gradients_train = strategy.experimental_run(train_step, train_iterator)

                dist_loss_train = [dist_loss_train.get(device) for device in dist_loss_train.devices]
                loss_train = tf.reduce_sum(dist_loss_train)

                accuracy_train = tf.reduce_mean(accuracy_train.values) # TODO: how to aggregate?

                layer_outputs_train = reduce_per_replica(layer_outputs_train)
                layer_gradients_train = reduce_per_replica(layer_gradients_train)
                layer_weights_train = reduce_per_replica(layer_weights_train)
                layer_biases_train = reduce_per_replica(layer_biases_train)
                
                ##### Validation statistics #####
                dist_loss_val, accuracy_val, \
                layer_outputs_val, layer_weights_val, layer_biases_val, \
                layer_gradients_val = strategy.experimental_run(validation_step, validation_iterator)

                dist_loss_val = dist_loss_val.values
                loss_val = tf.reduce_sum(dist_loss_val)

                accuracy_val = tf.reduce_mean(accuracy_val.values)
                layer_gradients_val = {k: v for k, v in layer_gradients_val.items() if v is not None}
                
                layer_outputs_val = reduce_per_replica(layer_outputs_val)
                layer_gradients_val = reduce_per_replica(layer_gradients_val)
                layer_weights_val = reduce_per_replica(layer_weights_val)
                layer_biases_val = reduce_per_replica(layer_biases_val)

                # Create an exportable version of the TensorFlow graph
                self._input_tensor_export = tf.placeholder(shape=[None] + dataset_trn.output_shapes[0].as_list(), dtype=dataset_trn.output_types[0])
                
                self._output_tensor_export = model(
                    self._input_tensor_export,
                    tf.placeholder(shape=[None] + dataset_trn.output_shapes[1].as_list(), dtype=dataset_trn.output_types[1])
                )[output_layer_id]
            else:
                #dist_loss, dist_grads_train, dist_locals = strategy.experimental_run(train_step, train_iterator)
                #dist_test = strategy.experimental_run(test_step, test_iterator) # TODO: implement this.

                raise NotImplementedError

            sess.run(tf.global_variables_initializer())
            
            if INCLUDE_KERAS_METRICS:
                sess.run([v.initializer for v in auc_train.variables])  # these need spec. treatment when initializing
                sess.run([v.initializer for v in recall_train.variables])
                sess.run([v.initializer for v in precision_train.variables])
                sess.run([v.initializer for v in auc_val.variables]) 
                sess.run([v.initializer for v in recall_val.variables])
                sess.run([v.initializer for v in precision_val.variables])
            else:
                auc_train_tensor = tf.constant(-1)
                auc_val_tensor = tf.constant(-2)
                f1_train = tf.constant(-3)
                f1_val = tf.constant(-4)   

            self._variables = {k: v for k, v in locals().items() if can_serialize(v)}        
            
            savables = tf.global_variables()
            self._savables=savables
            self._saver = tf.compat.v1.train.Saver(savables)

            # Restore from checkpoint if specified

            #import pdb; pdb.set_trace()      
            log.info("Entering training loop")

            self._epoch = 0
            while self._epoch < self._n_epochs and not self._stopped: 
                t0 = time.perf_counter()               
                self._training_iteration = 0
                self._validation_iteration = 0
                self._status = 'training'

                sess.run(train_iterator_init)                
                try:
                    while not self._stopped:
                        self._loss_training, self._accuracy_training, \
                            self._layer_outputs, self._layer_weights, self._layer_biases, \
                            self._layer_gradients = sess.run([loss_train, accuracy_train, layer_outputs_train, layer_weights_train, layer_biases_train, layer_gradients_train])         
                        
                        if INCLUDE_KERAS_METRICS:
                            auc_train.reset_states()
                            recall_train.reset_states()
                            precision_train.reset_states()     
                        yield YieldLevel.SNAPSHOT
                        self._training_iteration += 1 * n_devices
                except tf.errors.OutOfRangeError:
                    pass

                sess.run(validation_iterator_init)
                self._status = 'validation'
                try:
                    while not self._stopped:
                        self._loss_validation, self._accuracy_validation, \
                            self._layer_outputs, self._layer_weights, self._layer_biases, \
                            self._layer_gradients = sess.run([loss_val, accuracy_val, layer_outputs_val, layer_weights_val, layer_biases_val, layer_gradients_val])

                        if INCLUDE_KERAS_METRICS:
                            auc_val.reset_states()
                            recall_val.reset_states()
                            precision_val.reset_states()                                
                        yield YieldLevel.SNAPSHOT
                        self._validation_iteration += 1 * n_devices     
                except tf.errors.OutOfRangeError:
                    pass
                log.info(
                    f"Finished epoch {self._epoch+1}/{self._n_epochs} - "
                    f"loss training, validation: {self.loss_training:.6f}, {self.loss_validation:.6f} - "
                    f"acc. training, validation: {self.accuracy_training:.6f}, {self.accuracy_validation:.6f}"
                )
                log.info(f"Epoch duration: {round(time.perf_counter() - t0, 3)} s")            
                self._epoch += 1
            
            self._testing_iteration = 0
            self._status = 'testing'
            sess.run(test_iterator_init)
            x, y = test_iterator.get_next()
            layer_output_tensors = model(x, y)
            try:
                while not self._stopped:
                    self._layer_outputs = sess.run(layer_output_tensors)
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
            self._saver.save(self._sess, os.path.join(path, 'model.ckpt'), global_step=0)
                
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
    '_data_inputs': DataData_data_inputs(),
    '_data_labels': DataData_data_labels(),
    '_reshape': ProcessReshape_reshape(),
    '_one_hot': ProcessOneHot_one_hot(),
    '_fc': DeepLearningFC_fc(),
    '_training': TrainNormal_training(),
}

EDGES = {
    ('_data_inputs', '_reshape'),
    ('_data_labels', '_one_hot'),
    ('_reshape', '_fc'),
    ('_one_hot', '_training'),
    ('_fc', '_training'),
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
    print('Flask port: 5680')
    global graph, status, t_start, socket
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind('tcp://*:5681')
    log.addHandler(ZmqHandler())
    threading.Thread(target=app.run, kwargs={"port": "5680", "threaded": True}, daemon=True).start()
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
