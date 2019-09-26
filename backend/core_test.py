import tensorflow as tf
import numpy as np
import time
import copy 
from abc import ABC, abstractmethod
from collections import namedtuple

NET_CODE = """
X_tensor = tf.placeholder(tf.float32, [None, 2], name='X')
y_tensor = tf.placeholder(tf.float32, [None, 1], name='y')


W1 = tf.Variable(tf.truncated_normal(shape=[2,10], stddev=0.01))
b1 = tf.Variable(tf.constant(0.01))
z1 = tf.matmul(X_tensor, W1) + b1

W2 = tf.Variable(tf.truncated_normal(shape=[10,1], stddev=0.01))
b2 = tf.Variable(tf.constant(0.01))
z2 = tf.matmul(z1, W2) + b2

y = tf.nn.sigmoid(z2)
"""

DATA_CODE = """
y_ = np.array([[0], [1]], dtype=np.float32)
api.data.store_value('sample', X_[0])
"""


DATA_LAYER_X = """
Y = np.array([[1,2], [7,8]], dtype=np.float32)
api.data.store_value('sample', Y[0])

Y = tf.data.Dataset.from_tensor_slices(Y)
"""

DATA_LAYER_Y = """
Y = np.array([[0], [1]], dtype=np.float32)
api.data.store_value('sample', Y[0])

Y = tf.data.Dataset.from_tensor_slices(Y)
"""





CodePart = namedtuple('CodePart', ['name', 'code'])
    

class CodeGenerator(ABC):
    @abstractmethod
    def get_code(self):
        raise NotImplementedError

    def get_code_parts(self):
        code = self.get_code()        
        code_parts = [CodePart(name=None, code=code)]
        return code_parts
    

class CustomCodeGenerator(CodeGenerator):
    def __init__(self, input_):
        if isinstance(input_, str):
            self._code_parts = [CodePart(name=None, code=input_)]
        elif isinstance(input_, list) and all([isinstance(x, CodeParts) for x in input_]):
            self._code_parts = copy.copy(input_)
        else:
            raise ValueError("Inputs must be either string or list of CodeParts")

    def get_code_parts(self):
        return self._code_parts

    def get_code(self):
        code = ''
        for cp in self._code_parts:
            code += cp.code + '\n'            
        return code


TRAIN_TEMPLATE = """
cost = tf.reduce_mean(tf.square(y_tensor - y))
step = tf.train.%s(learning_rate=%f).minimize(cost)

sess = tf.InteractiveSession()
sess.run(tf.initialize_all_variables())

for epoch in range(%d):
    api.mode.set_training()
    api.data.store_value('epoch', epoch)

    for iter in range(%d):
        sess.run(step, feed_dict={X_tensor: X_, y_tensor: y_})

        api.data.store_value('iter', iter)
        api.ui.process()

    api.mode.set_validation()
    y_pred, cost_ = sess.run([y, cost], feed_dict={X_tensor: X_, y_tensor: y_})

    api.data.store_value('loss', cost_)
    api.data.store_value('iter', iter)
    api.ui.process()
"""

TEST_TEMPLATE = """
api.mode.set_testing()
y_pred = sess.run(y, feed_dict={X_tensor: X_})
api.data.store_value('y_pred', y_pred.squeeze())
api.ui.process()
"""

class TrainNormalCodeGenerator(CodeGenerator):
    def __init__(self, optimizer='adam', learning_rate=0.001):
        self._optimizer = optimizer
        self._learning_rate = learning_rate
        self._n_epochs = 300
        self._n_iters = 3

    def _get_training_code(self):
        if self._optimizer == 'adam':
            optimizer_class = 'AdamOptimizer'
        elif self._optimizer == 'adagrad':
            optimizer_class = 'AdagradOptimizer'

        code = TRAIN_TEMPLATE % (optimizer_class,
                                 self._learning_rate,
                                 self._n_epochs,
                                 self._n_iters)
        return code

    def _get_testing_code(self):
        return TEST_TEMPLATE

    def get_code_parts(self):
        cp1 = CodePart('training', self._get_training_code())
        cp2 = CodePart('testing', self._get_testing_code())
        return [cp1, cp2]

    def get_code(self):
        code = self._get_training_code() + '\n' + self._get_testing_code()
        return code

FULLY_CONNECTED_TEMPLATE = """
W1 = tf.Variable(tf.truncated_normal(shape=[%d,%d], stddev=0.01))
b1 = tf.Variable(tf.constant(0.01))
z1 = tf.matmul(X, W1) + b1
Y = tf.nn.%s(z1)
"""
    
class FullyConnectedCodeGenerator(CodeGenerator):
    def __init__(self, n_inputs, n_units, activation='relu'):
        self._n_inputs = n_inputs
        self._n_units = n_units
        self._activation = activation

    def get_code(self):
        code = FULLY_CONNECTED_TEMPLATE % (self._n_inputs, self._n_units, self._activation)
        return code
        

class ExecutionScope:
    def __init__(self, globals_, locals_=None):
        self._globals = copy.copy(globals_)
        self._locals = dict() if locals_ is None else copy.copy(locals_)
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    @property
    def locals(self):
        return copy.copy(self._locals)    

    @property
    def globals(self):
        return copy.copy(self._globals)

    def run(self, code):
        exec(code, self._globals, self._locals)

    def set_local(self, key, value):
        self._locals[key] = copy.copy(value)


class DataContainer:
    def __init__(self):
        self.reset()

    def reset(self):
        self._data_dict = dict()        

    def _create_subdict_if_needed(self, root_key):
        if not root_key in self._data_dict:
            self._data_dict[root_key] = dict()

    def store_value(self, root_key, name, value):
        self._create_subdict_if_needed(root_key)
        self._data_dict[root_key][name] = value

    def stack_value(self, root_key, name, value):
        self._create_subdict_if_needed(root_key)

        try:
            self._data_dict[root_key].append(value)
        except AttributeError:
            print("warning, overwriting existing value!")
            self._data_dict[root_key] = [value]
        except KeyError:
            self._data_dict[root_key] = [value]

    def to_dict(self):
        data_dict = copy.copy(self._data_dict)
        return data_dict

    def __getitem__(self, id_):
        data = copy.copy(self._data_dict.get(id_))
        return data

    def __contains__(self, id_):
        return id_ in self._data_dict


class DataPipe:
    # Class concerned with entering data correctly.
    def __init__(self, data_container):
        self.root_key = None
        self._container = data_container

    def store_value(self, name, value):
        if self.root_key is None:
            raise ValueError("root_key not set!")
        self._container.store_value(self.root_key, name, value)

    def stack_value(self, name, value):
        if self.root_key is None:
            raise ValueError("root_key not set!")        
        self._container.stack_value(self.root_key, name, value)
    

class UiChannel:
    def __init__(self, core_state, data_container, command_queue, result_queue):
        self._core_state = core_state
        self._data_container = data_container
        self._command_queue = command_queue
        self._result_queue = result_queue

    @property
    def has_new_command(self):
        return not self._command_queue.empty()

    def process(self):
        while self._core_state.is_paused or self.has_new_command:
            if self.has_command:
                command = self._command_queue.get()
                if command == 'pause':
                    self._core_state.set_paused()
                elif command == 'run':
                    self._core_state.set_running()

            if self._core_state.is_paused:
                time.sleep(0.3)

        # Do checkpoint stuff etc

        # put data_container on result queue?        
        from pprint import pprint
        pprint(self._data_container.to_dict())
        

class DataApi:
    def __init__(self, data_pipe):
        self._data = data_pipe

    def store_value(self, name, value):
        self._data.store_value(name, value)

    def stack_value(self, name, value):
        self._data.stack_value(name, value)

    
class UiApi:
    def __init__(self, ui_channel=None):
        self._ui_channel = ui_channel

    def process(self):
        if self._ui_channel is not None:
            self._ui_channel.process()


class ModeApi:
    def __init__(self, core_state=None):
        self._core_state = core_state

    def set_training(self):
        if self._core_state is not None:
            self._core_state.set_training()
        
    def set_validation(self):
        if self._core_state is not None:        
            self._core_state.set_validation()
        
    def set_testing(self):
        if self._core_state is not None:        
            self._core_state.set_testing()

        
class Api:
    def __init__(self, data, mode=None, ui=None):
        self._data = data

        if mode is None:
            mode = ModeApi(core_state=None)
        self._mode = mode

        if ui is None:
            ui = UiApi(ui_channel=None)        
        self._ui = ui 
        
    @property
    def data(self):
        return self._data

    @property
    def mode(self):
        return self._mode

    @property
    def ui(self):
        return self._ui        
    

class CoreState:
    CREATED = 'created'
    TRAINING_RUNNING = 'training_running'
    TRAINING_PAUSED = 'training_paused'    
    VALIDATION_RUNNING = 'validation_running'
    VALIDATION_PAUSED = 'validation_paused'    
    TESTING_RUNNING = 'testing_running'
    TESTING_PAUSED = 'testing_paused'    
    
    def __init__(self):
        self._state = self.CREATED

    def set_paused(self):
        if self._state == self.TRAINING_RUNNING:
            self._state = self.TRAINING_PAUSED
        elif self._state == self.VALIDATION_RUNNING:
            self._state = self.VALIDATION_PAUSED
        elif self._state == self.TESTING_RUNNING:
            self._state = self.TESTING_PAUSED
        else:
            raise RuntimeError("Cannot enter a state of type 'paused' from '{}'".format(self._state))        
    def set_running(self):
        if self._state == self.TRAINING_PAUSED:
            self._state = self.TRAINING_RUNNING
        elif self._state == self.VALIDATION_PAUSED:
            self._state = self.VALIDATION_RUNNING
        elif self._state == self.TESTING_PAUSED:
            self._state = self.TESTING_RUNNING
        else:
            raise RuntimeError("Cannot enter a state of type 'running' from '{}'".format(self._state))

    def set_training(self):
        if self._state == self.CREATED:
            self._state = self.TRAINING_RUNNING
        elif self._state == self.VALIDATION_RUNNING:
            self._state = self.TRAINING_RUNNING
        elif self._state == self.VALIDATION_PAUSED:
            self._state = self.TRAINING_PAUSED

        elif self._state == self.TRAINING_RUNNING:
            pass
        elif self._state == self.TRAINING_PAUSED:
            pass
            
        else:
            raise RuntimeError("Cannot enter a state of type 'training' from '{}'".format(self._state))                    
            
    def set_validation(self):
        if self._state == self.TRAINING_RUNNING:
            self._state = self.VALIDATION_RUNNING
        elif self._state == self.TRAINING_PAUSED:
            self._state = self.VALIDATION_PAUSED
        else:
            raise RuntimeError("Cannot enter a state of type 'validation' from '{}'".format(self._state))
        
    def set_testing(self):
        if self._state == self.TRAINING_RUNNING:
            self._state = self.TESTING_RUNNING
        elif self._state == self.TRAINING_PAUSED:
            self._state = self.TESTING_PAUSED
        elif self._state == self.VALIDATION_RUNNING:
            self._state = self.TESTING_RUNNING
        elif self._state == self.VALIDATION_PAUSED:
            self._state = self.TESTING_PAUSED
        else:
            raise RuntimeError("Cannot enter a state of type 'testing' from '{}'".format(self._state))

    @property
    def is_running(self):
        self._state in [self.TRAINING_RUNNING, self.VALIDATION_RUNNING, self.TESTING_RUNNING]
        
    @property
    def is_paused(self):
        self._state in [self.TRAINING_PAUSED, self.VALIDATION_PAUSED, self.TESTING_PAUSED]
        
    @property
    def is_training(self):
        self._state in [self.TRAINING_RUNNING, self.TRAINING_PAUSED]
        
    @property
    def is_validation(self):
        self._state in [self.VALIDATION_RUNNING, self.VALIDATION_PAUSED]
        
    @property
    def is_testing(self):
        self._state in [self.TESTING_RUNNING, self.TESTING_PAUSED]

        
class Core:
    def __init__(self, graph_dict, command_queue, result_queue):
        self._graph = self._build_graph(graph_dict)
        self._command_queue = command_queue
        self._result_queue = result_queue

    def run(self):        
        core_state = CoreState()        
        data_container = DataContainer()

        ui_channel = UiChannel(core_state, data_container, self._command_queue, self._result_queue)
        data_pipe = DataPipe(data_container)        

        # The APIs exposed to the user
        data_api = DataApi(data_pipe)
        mode_api = ModeApi(core_state)        
        ui_api = UiApi(ui_channel)
        api = Api(data_api, mode_api, ui_api)
        
        globals_ = {'tf': tf,
                    'np': np,
                    'api': api}

        with ExecutionScope(globals_) as e:
            for id_, code_generator in self._graph.items():
                data_pipe.root_key = id_
                code = code_generator.get_code()
                e.run(code)
        

    def _build_graph(self, graph_dict):
        return graph_dict # TODO: FIX THIS! SHOULD USE OLD GRAPH CODE.

    
LayerPreviewInfo = namedtuple('LayerPreviewInfo', ['Y', 'shape'])


class GraphPropagator:
    def __init__(self, graph_dict):
        self._graph = graph_dict
        #sess = tf.InteractiveSession()
        #sess.run(tf.initialize_all_variables())
        #self._sess = sess
        
    def propagate(self):        
        data_container = DataContainer()
        data_pipe = DataPipe(data_container)        

        # The APIs exposed to the user
        api = Api(DataApi(data_pipe))
        
        globals_ = {'tf': tf,
                    'np': np,
                    'api': api}
        outputs = {}

        graph_shortened = list(self._graph.items())[:-1]

        tf.enable_eager_execution()
        
        with ExecutionScope(globals_) as e:
            e.set_local('X', None)
            
            for id_, code_generator in graph_shortened:
                output = self._execute_layer(data_container, data_pipe, e, id_, code_generator)
                outputs[id_] = output
                
        tf.disable_eager_execution()
        
        return outputs
                    
    def _execute_layer(self, data_container, data_pipe, scope, id_, code_generator):
        data_pipe.root_key = id_
        code = code_generator.get_code()
        scope.run(code)

        Y = scope.locals['Y']

        if id_ in data_container and 'sample' in data_container[id_]:
            Y = np.atleast_2d(data_container[id_]['sample'])
                    
        scope.set_local('X', Y)
        output = Y
        return output
        
                    

                    
    
if __name__ == "__main__":
    import queue

    data_x = CustomCodeGenerator(DATA_LAYER_X)
    data_y = CustomCodeGenerator(DATA_LAYER_Y)    

    fc1 = FullyConnectedCodeGenerator(2, 10)
    fc2 = FullyConnectedCodeGenerator(10, 1, activation='sigmoid')    
    
    network = CustomCodeGenerator(NET_CODE)
    data = CustomCodeGenerator(DATA_CODE)
    train = TrainNormalCodeGenerator(optimizer='adam', learning_rate=0.001)
    
    #graph = {'0': data, '1': network, '2': train}

    graph = {'0': data_x, '1': fc1, '2': fc2, '3': train}
    
    for id_, cg in graph.items():
        print("Layer with id {}".format(id_))
        print(cg.get_code())


    gp = GraphPropagator(graph)
    output = gp.propagate()

    from pprint import pprint
    pprint(output)

    #raise SystemExit

    #import pdb; pdb.set_trace()

    cc = queue.Queue()
    rc = queue.Queue()
    
    core = Core(graph, cc, rc)
    core.run()
    

