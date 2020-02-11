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
        matrix_DataData_data_inputs_0 = np.load("C:/Users/Robert/AppData/Local/Temp/tmpcvnl1jyl.npy").astype(np.float32)
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


class DataData_data_labels(DataLayer):
    """Class responsible for loading data from files (e.g., numpy, csv, etc)."""    
    def __init__(self):
        self._variables = {}
        
        columns = {}
        trn_sz_tot, val_sz_tot, tst_sz_tot = 0, 0, 0        
        trn_gens_args_DataData_data_labels, val_gens_args_DataData_data_labels, tst_gens_args_DataData_data_labels = [], [], []        

        

        columns_DataData_data_labels_0 = None
    
        global matrix_DataData_data_labels_0
        matrix_DataData_data_labels_0 = np.load("C:/Users/Robert/AppData/Local/Temp/tmprfcwuckz.npy").astype(np.float32)
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
            
        self._variables = {k: v for k, v in locals().items() if dill.pickles(v)}            
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
        self._status = 'initializing'        

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

        output_tensor = layer_output_tensors[output_layer_id]
        target_tensor = layer_output_tensors[target_layer_id]

        loss_tensor = tf.reduce_mean(tf.square(output_tensor - target_tensor))
        correct_predictions = tf.equal(tf.argmax(output_tensor, -1), tf.argmax(target_tensor, -1))
        accuracy_tensor = tf.reduce_mean(tf.cast(correct_predictions, tf.float32))

        global_step = None

        optimizer = tf.compat.v1.train.GradientDescentOptimizer(learning_rate=0.5)

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
                    gradients[name] = grad_tensor
                layer_gradient_tensors[node.layer_id] = gradients
                self._layer_gradients[node.layer_id] = {name: [] for name in node.layer.trainable_variables.keys()} # Initialize
        
        trainable_vars = tf.trainable_variables()
        grads = tf.gradients(loss_tensor, trainable_vars)
        update_weights = optimizer.apply_gradients(zip(grads, trainable_vars), global_step=global_step)        

        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        sess = tf.Session(config=config)
        self._saver = tf.train.Saver()
        sess.run(tf.global_variables_initializer())

        def sleep_while_paused():
            while self._paused:
                time.sleep(1.0)

        def train_step():
            _, self._loss_training, self._accuracy_training, \
                self._layer_outputs, self._layer_weights, self._layer_biases, \
                self._layer_gradients \
                = sess.run([
                    update_weights, loss_tensor, accuracy_tensor,
                    layer_output_tensors, layer_weight_tensors, layer_bias_tensors, layer_gradient_tensors
                ])
            
        def validation_step():
            self._loss_validation, self._accuracy_validation, \
                self._layer_outputs, self._layer_weights, self._layer_biases, \
                self._layer_gradients \
                = sess.run([
                    loss_tensor, accuracy_tensor,
                    layer_output_tensors, layer_weight_tensors, layer_bias_tensors, layer_gradient_tensors
                ])

            
        def test_step():
            self._loss_testing, self._accuracy_testing, \
                self._layer_outputs, self._layer_weights, layer_gradients \
                = sess.run([
                    loss_tensor, accuracy_tensor,
                    layer_output_tensors, layer_weight_tensors, layer_gradient_tensors
                ])
            #accuracy_list.append(acc)
            #loss_list.append(loss)

        self._variables = {k: v for k, v in locals().items() if dill.pickles(v)}

        log.info("Entering training loop")
        
        # Training loop
        self._epoch = 0
        while self._epoch < self._n_epochs:
            self._training_iteration = 0
            self._status = 'training'
            sess.run(trn_init)            
            try:
                while not self._stopped:
                    sleep_while_paused()
                    train_step()
                    self.save_snapshot(graph)
                    self._training_iteration += 1
            except tf.errors.OutOfRangeError:
                pass


            self._validation_iteration = 0
            self._status = 'validation'
            sess.run(val_init)            
            try:
                while not self._stopped:
                    sleep_while_paused()
                    validation_step()
                    self.save_snapshot(graph)                    
                    self._validation_iteration += 1
            except tf.errors.OutOfRangeError:
                pass


            log.info(
                f"Finished epoch {self._epoch+1}/{self._n_epochs} - "
                f"loss training, validation: {self.loss_training:.6f}, {self.loss_validation:.6f} - "
                f"acc. training, validation: {self.accuracy_training:.6f}, {self.accuracy_validation:.6f}"
            )


            print(
                f"Finished epoch {self._epoch+1}/{self._n_epochs} - "
                f"loss training, validation: {self.loss_training:.6f}, {self.loss_validation:.6f} - "
                f"acc. training, validation: {self.accuracy_training:.6f}, {self.accuracy_validation:.6f}"
            )

            self._epoch += 1

        self._variables = {k: v for k, v in locals().items() if dill.pickles(v)}            
            
        # Test loop
        self._testing_iteration = 0
        self._status = 'testing'
        sess.run(tst_init)                                
        try:
            while not self._stopped:
                sleep_while_paused()
                test_step()
                self.save_snapshot(graph)                                    
                self._testing_iteration += 1
        except tf.errors.OutOfRangeError:
            pass

        self._status = 'finished'
        self._variables = {k: v for k, v in locals().items() if dill.pickles(v)}
        self.save_snapshot(graph)        

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
    '_reshape': ProcessReshape_reshape(),
    '_data_labels': DataData_data_labels(),
    '_fc': DeepLearningFC_fc(),
    '_one_hot': ProcessOneHot_one_hot(),
    '_training': TrainNormal_training(),
}

EDGES = {
    ('_data_inputs', '_reshape'),
    ('_reshape', '_fc'),
    ('_data_labels', '_one_hot'),
    ('_fc', '_training'),
    ('_one_hot', '_training'),
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