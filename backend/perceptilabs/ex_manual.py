''' Manually written example of scriptbuilder output '''

import time
import logging
import numpy as np
import tensorflow as tf


from code.layer import InnerLayer, TrainingSupervised, DataSupervised, Tf1xLayer
from core_new.graph import Graph, Node
from core_new.api.logging import CoreHandler
from core_new.api.mapping import ByteMap, EventBus

state_mapping = dict()


ZMQ_DEALER_ADDRESS = ''
ZMQ_SUBSCRIBER_ADDRESS = ''
ZMQ_PUSH_ADDRESS = ''

event_bus = EventBus('event_bus', ZMQ_DEALER_ADDRESS, ZMQ_SUBSCRIBER_ADDRESS, ZMQ_PUSH_ADDRESS)
state_map = ByteMap('state_map', ZMQ_DEALER_ADDRESS, ZMQ_SUBSCRIBER_ADDRESS, ZMQ_PUSH_ADDRESS)

log = logging.getLogger(__name__)
log.addHandler(CoreHandler(event_bus))


class RandomDataLayer1(DataSupervised):
    def __init__(self):
        self._data = np.random.random((100, 784))

    @property
    def variables(self):
        return {}

    @property
    def sample(self):
        return self._data[0]

    @property
    def size_training(self):
        return 70

    @property
    def size_validation(self):
        return 20

    @property
    def size_testing(self):
        return 10

    def make_generator_training(self):
        yield from self._data[0:70]
        
    def make_generator_validation(self):
        yield from self._data[70:90]
        
    def make_generator_testing(self):
        yield from self._data[90:]    


class RandomDataLayer2(DataSupervised):
    def __init__(self):
        self._data = np.random.randint(0, 10, (100,))

    @property
    def variables(self):
        return {}

    @property
    def sample(self):
        return self._data[0]

    @property
    def size_training(self):
        return 70

    @property
    def size_validation(self):
        return 20

    @property
    def size_testing(self):
        return 10

    def make_generator_training(self):
        yield from self._data[0:70]
        
    def make_generator_validation(self):
        yield from self._data[70:90]
        
    def make_generator_testing(self):
        yield from self._data[90:]

        
class FullyConnected3(Tf1xLayer):
    def __init__(self):
        self._n_neurons = 10
        
    def __call__(self, x):
        n_neurons = self._n_neurons
        n_inputs = np.prod(x.get_shape().as_list()[1:], dtype=np.int32)

        initial = tf.truncated_normal((n_inputs, self._n_neurons), stddev=0.1)
        W = tf.Variable(initial)
        
        initial = tf.constant(0.1, shape=[self._n_neurons])
        b = tf.Variable(initial)
        flat_node = tf.cast(tf.reshape(x, [-1, n_inputs]), dtype=tf.float32)
        y = tf.matmul(flat_node, W) + b
        return y

    @property
    def variables(self):
        return []

    @property
    def trainable_variables(self):
        return []
    
    
class OneHot4(Tf1xLayer):
    def __init__(self):
        self._n_classes = 10

    def __call__(self, x):
        y = tf.one_hot(tf.cast(x, dtype=tf.int32), self._n_classes)
        return y        

    @property
    def variables(self):
        return []

    @property
    def trainable_variables(self):
        return []

    
class TrainNormalLayer(TrainingSupervised):
    def __init__(self, output_layer: InnerLayer, target_layer: InnerLayer):
        """ Generated according to layer properties [true for all layers] """
        self._training_status = 'created'        
        self._output_layer = output_layer
        self._target_layer = target_layer
    
    def run(self, graph: Graph):
        self._training_status = 'initializing'
        input_data_layers = graph.get_data_dependencies(self._output_layer)
        label_data_layers = graph.get_data_dependencies(self._target_layer)

        assert len(input_data_layers) == 1
        assert len(label_data_layers) == 1
        input_data_layer = input_data_layers[0]
        label_data_layer = label_data_layers[0]        

        # Make training set
        dataset_trn = tf.data.Dataset.zip((
            tf.data.Dataset.from_generator(
                input_data_layer.make_generator_training,
                output_shapes=input_data_layer.sample.shape,
                output_types=np.float32                
            ),
            tf.data.Dataset.from_generator(
                label_data_layer.make_generator_training,
                output_shapes=label_data_layer.sample.shape,
                output_types=np.float32
            )
        ))

        # Make validation set
        dataset_val = tf.data.Dataset.zip((
            tf.data.Dataset.from_generator(
                input_data_layer.make_generator_validation,
                output_shapes=input_data_layer.sample.shape,
                output_types=np.float32                
            ),
            tf.data.Dataset.from_generator(
                label_data_layer.make_generator_validation,
                output_shapes=label_data_layer.sample.shape,
                output_types=np.float32
            )
        ))

        # Make testing set
        dataset_tst = tf.data.Dataset.zip((
            tf.data.Dataset.from_generator(
                input_data_layer.make_generator_testing,
                output_shapes=input_data_layer.sample.shape,
                output_types=np.float32                
            ),
            tf.data.Dataset.from_generator(
                label_data_layer.make_generator_testing,
                output_shapes=label_data_layer.sample.shape,
                output_types=np.float32
            )
        ))

        batch_size = 8
        dataset_trn = dataset_trn.batch(batch_size)
        dataset_val = dataset_val.batch(batch_size)
        dataset_tst = dataset_tst.batch(1)                

        # Make initializers
        iterator = tf.data.Iterator.from_structure(dataset_trn.output_types,
                                                   dataset_trn.output_shapes)
        trn_init = iterator.make_initializer(dataset_trn)
        val_init = iterator.make_initializer(dataset_val)
        tst_init = iterator.make_initializer(dataset_tst)
        
        input_tensor, label_tensor = iterator.get_next()

        # Build the TensorFlow graph
        layer_outputs = {
            input_data_layer: input_tensor,
            label_data_layer: label_tensor
        }
        
        for node in graph.inner_nodes.values():
            args = []
            for input_layer in node.inputs:
                args.append(layer_outputs[input_layer])
            y = node.layer(*args)
            layer_outputs[node.layer] = y

        output_tensor = layer_outputs[self._output_layer]
        target_tensor = layer_outputs[self._target_layer]
            
        sess = tf.Session()
        self._saver = tf.train.Saver()
        sess.run(tf.global_variables_initializer())
        sess.run(trn_init)

        def sleep_while_paused():
            while self._paused:
                time.sleep(1.0)

        def train_step():
            pass
        
        def validation_step():
            pass

        def test_step():
            pass
        
        # Training loop
        self._epoch = 0
        while self._epoch < self._n_epochs:
            self._iteration = 0
            self._training_status = 'training'
            try:
                while not self._stopped:
                    sleep_while_paused()
                    train_step()
                    self.send_state_updates(graph)
                    self._iteration += 1
            except tf.errors.OutOfRangeError:
                pass

            self._training_status = 'validation'            
            try:
                while not self._stopped:
                    sleep_while_paused()
                    validation_step()
                    self.send_state_updates(graph)                    
                    self._iteration += 1
            except tf.errors.OutOfRangeError:
                pass
            
            self._epoch += 1

        # Test loop
        self._iteration = 0
        self._training_status = 'testing'                    
        try:
            while not self._stopped:
                sleep_while_paused()
                test_step()
                self.send_state_updates(graph)                                    
                self._iteration += 1
        except tf.errors.OutOfRangeError:
            pass

        self._training_status = 'finished'                            

    def on_pause(self):
        self._paused = True

    def on_resume(self):
        self._paused = False

    def on_stop(self):
        self._stopped = True

    def on_save(self):
        # TODO: Call ._saver, verify thread-safety
        pass

    def on_load(self):
        # TODO: for loading weights
        pass

    @property
    def training_status(self):
        # training, valdation, testing, etc.
        pass
    
    @property
    def epoch(self):
        return 0

    @property
    def iteration(self):
        return 0

    @property
    def variables(self):
        return {}

    @property
    def sample(self) -> np.ndarray:
        return None

    @property
    def size_training(self):
        return 0

    @property
    def size_validation(self):
        return 0

    @property
    def size_testing(self):
        return 0

    def make_generator_training(self):
        # Simply call sess.run on the output & target tensors :)  #TODO: how to make generators generic? We have two datasets here, but not all datasets will be labeled. Distinguish between supervised/unsupervised data layers and instead require pairs of data layers for supervised?
        yield from []
        
    def make_generator_validation(self):
        yield from []
        
    def make_generator_testing(self):
        yield from []
        
            
if __name__ == "__main__":
    l1 = RandomDataLayer1()
    l2 = RandomDataLayer2()
    l3 = FullyConnected3()
    l4 = OneHot4()

    graph = Graph({
        l1: Node(l1, ()),
        l2: Node(l2, ()),
        l3: Node(l3, (l1,)),
        l4: Node(l4, (l2,))                        
    })

    def on_event(training_layer, value):
        # TODO: this switch should be dynamically generated depending on the type of training layer. Consider using decorators for specification?
        # Perhaps it only makes sense to support our base layers, and custom layers are gonna have to rely on 'variables', etc. They don't have UI support anyway.        
        if value == 'stop':
            training_layer.on_stop()
            
    def send_state_updates(graph):
        # PASSED TO TRAINING LAYER
        for node in graph.nodes:
            # TODO: this switch should be dynamically generated depending on which layers are present. Consider using decorators for specification? or just take all properties?
            # Perhaps it only makes sense to support our base layers, and custom layers are gonna have to rely on 'variables', etc. They don't have UI support anyway.
            layer = node.layer
            if isinstance(layer, DataSupervised):
                state_mapping['size_training'] = layer.size_training
                state_mapping['sample'] = layer.sample
            elif isinstance(node.layer, Tf1xLayer):
                pass
            elif isinstance(layer, TrainingSupervised):
                pass

    
    tl = TrainNormalLayer(l3, l4)

    tl.set_on_state_update_handler(send_state_updates)    
    event_bus.set_on_event(lambda value: on_event(tl, value.decode('utf-8')))
    
    tl.run(graph)



        

        
        

