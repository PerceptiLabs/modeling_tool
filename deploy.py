import tensorflow as tf
import numpy as np
import dill
import sys
import json
import time
import zlib
import logging
import threading
from typing import Dict, Any, List, Tuple, Generator
from flask import Flask, jsonify
import flask

from perceptilabs.core_new.utils import Picklable
from perceptilabs.core_new.layers import *
from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP, REPLICATED_PROPERTIES_TABLE
from perceptilabs.core_new.graph import Graph
from perceptilabs.core_new.graph.builder import GraphBuilder, SnapshotBuilder
from perceptilabs.core_new.api.mapping import MapServer, ByteMap


logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)
global graph
graph = None


class DataData_data_inputs(DataLayer):
    """Class responsible for loading data from files (e.g., numpy, csv, etc)."""    
    def __init__(self):
        self._variables = {}
        
        columns = {}
        trn_sz_tot, val_sz_tot, tst_sz_tot = 0, 0, 0        
        trn_gens_args_DataData_data_inputs, val_gens_args_DataData_data_inputs, tst_gens_args_DataData_data_inputs = [], [], []        

        

        columns_DataData_data_inputs_0 = None
    
        global matrix_DataData_data_inputs_0
        matrix_DataData_data_inputs_0 = np.load("C:/Users/Robert/AppData/Local/Temp/tmpraqisylq.npy").astype(np.float32)
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
                    
        self._variables = {k: v for k, v in locals().items() if dill.pickles(v)}

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
        matrix_DataData_data_labels_0 = np.load("C:/Users/Robert/AppData/Local/Temp/tmpoknsx2rf.npy").astype(np.float32)
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
                    
        self._variables = {k: v for k, v in locals().items() if dill.pickles(v)}

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
    def variables(self):
        """Any variables belonging to this layer that should be rendered in the frontend.
        
        Returns:
            A dictionary with tensor names for keys and picklable for values.
        """
        return {}

    @property
    def trainable_variables(self):
        """Any trainable variables belonging to this layer that should be updated during backpropagation. Their gradients will also be rendered in the frontend.
        
        Returns:
            A dictionary with tensor names for keys and tensors for values.
        """
        return {}

    @property
    def weights(self):
        """Any weight tensors belonging to this layer that should be rendered in the frontend.

        Return:
            A dictionary with tensor names for keys and tensors for values.
        """        
        return {}

    @property    
    def biases(self):
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

        self._variables = {}
        for k, v in locals().items():
            save = False
            try:
                save = dill.pickles(v)
            except:
                pass
            if save:
                self._variables[k] = v
        # self._variables = {k: v for k, v in locals().items() if try: dill.pickles(v); except: }            
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
        self._n_epochs = 100
        self._batch_size = 10 # TODO: ?

        self._stopped = False
        self._paused = False
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

        # Set Devices and Distribution Strategy
        n_devices = 4
        config = tf.ConfigProto(device_count={"CPU": n_devices, "GPU": 0},
                               gpu_options={"allow_growth": True},
                               inter_op_parallelism_threads=n_devices,
                               intra_op_parallelism_threads=1)
        # config = tf.ConfigProto(gpu_options={"allow_growth": True}, log_device_placement=True, allow_soft_placement=True)

        sess = tf.Session(config=config)
        tf.keras.backend.set_session(sess) # since we use keras metrics

        strategy = tf.distribute.MirroredStrategy(devices=[f'/CPU:{i}' for i in range(n_devices)]) # TODO: not needed under real circumstances, should default to all.

        BATCH_SIZE_PER_REPLICA = 10 # TODO: get from frontend/json network
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
        test_dataset = dataset_tst.batch(1)                

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
            optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.01*n_devices) # lr proportional to batch size per linear scaling rule

            def sleep_while_paused():
                while self._paused:
                    time.sleep(1.0)

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
                    layer_weight_tensors[node.layer_id] = node.layer.weights
                    layer_bias_tensors[node.layer_id] = node.layer.biases            
                    
                    if len(node.layer.trainable_variables) > 0:
                        gradients = {}
                        for name, tensor in node.layer.trainable_variables.items():
                            grad_tensor = tf.gradients(loss_tensor, tensor)
                            if any(x is None for x in grad_tensor):
                                grad_tensor = tf.constant(0)
                            if len(grad_tensor) == 1:
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
                    return tf.identity(loss_tensor), accuracy_tensor, layer_output_tensors, layer_weight_tensors, layer_bias_tensors, layer_gradient_tensors

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
                            if len(grad_tensor) == 1:
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
                    return tf.identity(loss_tensor), accuracy_tensor, layer_output_tensors, layer_weight_tensors, layer_bias_tensors, layer_gradient_tensors

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

            else:
                #dist_loss_train, dist_grads_train, dist_locals = strategy.experimental_run(train_step, train_iterator)
                #dist_test = strategy.experimental_run(test_step, test_iterator) # TODO: implement this.
                pass

            sess.run(tf.global_variables_initializer())
            
            if INCLUDE_KERAS_METRICS:
                sess.run([v.initializer for v in auc_train.variables])  # these need spec. treatment when initializing
                sess.run([v.initializer for v in recall_train.variables])
                sess.run([v.initializer for v in precision_train.variables])
                sess.run([v.initializer for v in auc_val.variables]) 
                sess.run([v.initializer for v in recall_val.variables])
                sess.run([v.initializer for v in precision_val.variables])

            
            if not INCLUDE_KERAS_METRICS:
                auc_train_tensor = tf.constant(-1)
                auc_val_tensor = tf.constant(-2)
                f1_train = tf.constant(-3)
                f1_val = tf.constant(-4)     

            # self._variables = {k: v for k, v in locals().items() if dill.pickles(v)} 
            self._variables= {}
            for k, v in locals().items():
                try:
                    if dill.pickles(v):
                        self._variables[k] = v
                except:
                    pass

            self._epoch = 0
            while self._epoch < self._n_epochs:
                self._training_iteration = 0
                self._status = 'training'

                sess.run(train_iterator_init)
                
                try:
                    while not self._stopped:
                        sleep_while_paused()

                        self._loss_training, self._accuracy_training, \
                        self._layer_outputs, self._layer_weights, self._layer_biases, \
                        self._layer_gradients = sess.run([loss_train, accuracy_train, layer_outputs_train, layer_weights_train, layer_biases_train, layer_gradients_train]) 

                        print("Training Acc: ", self._accuracy_training)

                        if INCLUDE_KERAS_METRICS:
                            auc_train.reset_states()
                            recall_train.reset_states()
                            precision_train.reset_states()    

                        # self.save_snapshot(graph)                            
                        
                        self._training_iteration += 1
                except tf.errors.OutOfRangeError:
                    pass

                sess.run(validation_iterator_init)

                self._validation_iteration = 0
                self._status = 'validation'
                try:
                    while True:
                        sleep_while_paused()

                        self._loss_validation, self._accuracy_validation, \
                        self._layer_outputs, self._layer_weights, self._layer_biases, \
                        self._layer_gradients = sess.run([loss_val, accuracy_val, layer_outputs_val, layer_weights_val, layer_biases_val, layer_gradients_val])

                        print("Val Acc: ", self._accuracy_validation)

                        if INCLUDE_KERAS_METRICS:
                            auc_val.reset_states()
                            recall_val.reset_states()
                            precision_val.reset_states()                                

                        # self.save_snapshot(graph)  
                        
                        self._validation_iteration += 1            
                except tf.errors.OutOfRangeError:
                    pass


            sess.run(test_iterator_init)
            iter = 0
            x, y = test_iterator.get_next()    
            y_pred, y_target = model(x, y)

            # all tensors test
            model._locals = {}
            locals_ = model._locals.copy()
            locals_[input_data_layer] = {'Y': x} # output/preview. hack hack hack
            locals_[target_data_layer] = {'Y': y} # this layer is not run here.....:/
            
            locals_[self_layer_name] = {'X': {
                output_layer: {'Y': y_target}, # inputs to this layer...
                target_layer: {'Y': y_pred}
            }}
            
            all_tensors_test = get_tensors(locals_)
            try:
                while True:
                    all_evaled_tensors = sess.run(all_tensors_test)
                    api.data.store(all_tensors=all_evaled_tensors)
                    api.data.store(iter_testing=iter)
                    iter+=1
                    api.ui.render(dashboard='testing')  
            except tf.errors.OutOfRangeError:      
                pass

                

    def on_pause(self):
        """Called when the pause button is clicked in the frontend. 
        It is up to the implementing layer to pause its execution. 

        CAUTION: This method will be called from a different thread than run - keep thread-safety in mind."""
        self._paused = True

    def on_resume(self):
        """Called when the resume button is clicked in the frontend. 
        It is up to the implementing layer to resume execution. 
        
        CAUTION: This method will be called from a different thread than run - keep thread-safety in mind."""
        self._paused = False

    def on_save(self):
        """Called when the resume button is clicked in the frontend. 
        It is up to the implementing layer to save the model to disk.
        
        CAUTION: This method will be called from a different thread than run - keep thread-safety in mind."""
        # TODO: Call ._saver, verify thread-safety
        pass

    def on_stop(self):
        """Called when the save model button is clicked in the frontend. 
        It is up to the implementing layer to save the model to disk.
        
        CAUTION: This method will be called from a different thread than run - keep thread-safety in mind."""
        self._stopped = True

    @property
    def is_paused(self):
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

snapshots = []
snapshot_lock = threading.Lock()

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
         non_picklable = boltons.iterutils.research(snapshots[index], query=lambda p, k, v: type(v) not in [list, dict, set, tuple] and not dill.pickles(v))
         if non_picklable:
             print('not picklable:', non_picklable)
         raise
@app.route('/command', methods=['POST'])
def endpoint_event():
    from flask import request
    data = request.json
    if data['type'] == 'on_pause':
        graph.active_training_node.layer.on_pause()
    elif data['type'] == 'on_resume':
        graph.active_training_node.layer.on_resume()
    return jsonify(success=True)
snapshot_builder = SnapshotBuilder(
    BASE_TO_REPLICA_MAP, 
    REPLICATED_PROPERTIES_TABLE
)

def make_snapshot(graph):
    global snapshot_lock, snapshots
    with snapshot_lock:
        snapshot = snapshot_builder.build(graph)
        snapshots.append(snapshot)
def main():
    global graph
    threading.Thread(target=app.run, kwargs={"port": 5678}, daemon=True).start()
    graph_builder = GraphBuilder()
    graph = graph_builder.build(LAYERS, EDGES)
    
    print(graph.training_nodes)
    graph.training_nodes[0].layer_instance.save_snapshot = make_snapshot
    graph.training_nodes[0].layer_instance.run(graph)
    time.sleep(10)


if __name__ == "__main__":
    main()