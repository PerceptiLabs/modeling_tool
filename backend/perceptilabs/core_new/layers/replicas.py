import tensorflow as tf
from typing import List, Callable


from perceptilabs.core_new.layers import DataLayer, DataSupervised, DataRandom, DataReinforce, DataSupervised, Tf1xLayer, ClassificationLayer, InnerLayer, RegressionLayer, ObjectDetectionLayer, RLLayer, GANLayer


class NotReplicatedError(Exception):
    pass

class DataLayerReplica(DataLayer):
    def __init__(self, variables, sample):
        self._variables = variables
        self._sample = sample
    @property
    def variables(self):
        return self._variables

    @property
    def sample(self):
        return self._sample

class DataSupervisedReplica(DataSupervised):
    def __init__(self, sample, size_training, size_validation, size_testing, variables, columns):
        self._sample = sample
        self._size_training = size_training
        self._size_validation = size_validation
        self._size_testing = size_testing
        self._variables = variables
        self._columns = columns        

    @property
    def sample(self):
        return self._sample 

    @property
    def columns(self):
        return self._columns
    
    @property
    def size_training(self):
        return self._size_training 

    @property
    def size_validation(self):
        return self._size_validation

    @property
    def size_testing(self):
        return self._size_testing 

    @property        
    def variables(self):
        return self._variables 
    
    def make_generator_training(self):
        raise NotReplicatedError

    def make_generator_validation(self):
        raise NotReplicatedError        

    def make_generator_testing(self):
        raise NotReplicatedError

class DataRandomReplica(DataRandom):
    def __init__(self, sample, size_training, size_validation, size_testing, variables, columns):
        self._sample = sample
        self._size_training = size_training
        self._size_validation = size_validation
        self._size_testing = size_testing
        self._variables = variables
        self._columns = columns        

    @property
    def sample(self):
        return self._sample 

    @property
    def columns(self):
        return self._columns
    
    @property
    def size_training(self):
        return self._size_training 

    @property
    def size_validation(self):
        return self._size_validation

    @property
    def size_testing(self):
        return self._size_testing 

    @property        
    def variables(self):
        return self._variables 
    
    def make_generator_training(self):
        raise NotReplicatedError

    def make_generator_validation(self):
        raise NotReplicatedError        

    def make_generator_testing(self):
        raise NotReplicatedError

class DataReinforceReplica(DataReinforce):
    def __init__(self, sample, variables, action_space):
        self._sample = sample
        self._variables = variables
        self._action_space = action_space
    
    @property
    def variables(self):
        return self._variables 
    
    @property
    def sample(self):
        return self._sample 

    @property
    def action_space(self):
        return self._action_space
    
    def reset_environment(self, generator):
        raise NotReplicatedError

    def make_generator(self):
        raise NotReplicatedError

    def take_action(self, generator, action):
        raise NotReplicatedError
  
class ClassificationLayerReplica(ClassificationLayer):
    def __init__(self, sample, size_training, size_validation, size_testing, variables,
                 accuracy_training, accuracy_testing, accuracy_validation,
                 loss_training, loss_testing, loss_validation,
                 status, layer_weights, layer_biases, layer_gradients, layer_outputs,
                 batch_size, training_iteration, validation_iteration,
                 testing_iteration, progress, epoch, export_modes, columns):

        self._export_modes = export_modes
        self._epoch = epoch
        self._sample = sample
        self._columns = columns        
        self._size_training = size_training
        self._size_validation = size_validation        
        self._size_testing = size_testing
        self._variables = variables
        self._accuracy_training = accuracy_training 
        self._accuracy_validation = accuracy_validation
        self._accuracy_testing = accuracy_testing
        self._loss_training = loss_training
        self._loss_validation = loss_validation
        self._loss_testing = loss_testing
        self._status = status

        self._layer_weights = layer_weights
        self._layer_biases = layer_biases
        self._layer_gradients = layer_gradients
        self._layer_outputs = layer_outputs

        self._batch_size = batch_size
        self._training_iteration = training_iteration
        self._validation_iteration = validation_iteration
        self._testing_iteration = testing_iteration
        self._progress = progress

    @property
    def epoch(self):
        return self._epoch
    
    @property
    def batch_size(self):
        return self._batch_size
    
    @property
    def sample(self):
        return self._sample 

    @property
    def columns(self):
        return self._columns
    
    @property
    def size_training(self):
        return self._size_training 

    @property
    def size_validation(self):
        return self._size_validation

    @property
    def size_testing(self):
        return self._size_testing 

    @property        
    def variables(self):
        return self._variables 

    @property
    def accuracy_training(self):
        return self._accuracy_training

    @property
    def accuracy_testing(self):
        return self._accuracy_testing

    @property
    def accuracy_validation(self):
        return self._accuracy_validation

    @property
    def loss_training(self):
        return self._loss_training

    @property
    def loss_testing(self):
        return self._loss_testing

    @property
    def loss_validation(self):
        return self._loss_validation
        
    @property
    def status(self):
        return self._status

    @property
    def layer_weights(self):
        return self._layer_weights
    
    @property
    def layer_biases(self):
        return self._layer_biases
    
    @property
    def layer_gradients(self):
        return self._layer_gradients

    @property
    def layer_outputs(self):
        return self._layer_outputs

    def make_generator_training(self):
        raise NotReplicatedError

    def make_generator_validation(self):
        raise NotReplicatedError        

    def make_generator_testing(self):
        raise NotReplicatedError

    def on_stop(self):
        raise NotReplicatedError        
    
    def on_export(self, path):
        raise NotReplicatedError
    
    @property
    def training_iteration(self):
        return self._training_iteration

    @property
    def validation_iteration(self):
        return self._validation_iteration

    @property
    def testing_iteration(self):
        return self._testing_iteration

    @property
    def progress(self):
        return self._progress

    @property
    def export_modes(self):
        return self._export_modes
        
class RegressionLayerReplica(RegressionLayer):
    def __init__(self, sample, size_training, size_validation, size_testing, variables,
                 loss_training, loss_testing, loss_validation,
                 squared_error_training, squared_error_testing, squared_error_validation,
                 squared_variance_training, squared_variance_testing, squared_variance_validation,
                 r_squared_training, r_squared_testing, r_squared_validation,
                 status, layer_weights, layer_biases, layer_gradients, layer_outputs,
                 batch_size, training_iteration, validation_iteration,
                 testing_iteration, progress, epoch, export_modes, columns):

        self._export_modes = export_modes
        self._epoch = epoch
        self._sample = sample
        self._size_training = size_training
        self._size_validation = size_validation        
        self._size_testing = size_testing
        self._variables = variables
        self._loss_training = loss_training
        self._loss_validation = loss_validation
        self._loss_testing = loss_testing
        self._squared_error_training = squared_error_training
        self._squared_error_validation = squared_error_validation
        self._squared_error_testing = squared_error_testing
        self._squared_variance_training = squared_variance_training
        self._squared_variance_testing = squared_variance_testing
        self._squared_variance_validation = squared_variance_validation
        self._r_squared_training = r_squared_training
        self._r_squared_testing = r_squared_testing
        self._r_squared_validation = r_squared_validation 
        self._status = status
        self._columns = columns 

        self._layer_weights = layer_weights
        self._layer_biases = layer_biases
        self._layer_gradients = layer_gradients
        self._layer_outputs = layer_outputs

        self._batch_size = batch_size
        self._training_iteration = training_iteration
        self._validation_iteration = validation_iteration
        self._testing_iteration = testing_iteration
        self._progress = progress

    @property
    def columns(self):
        return self._columns

    @property
    def epoch(self):
        return self._epoch
    
    @property
    def sample(self):
        return self._sample 

    @property
    def size_training(self):
        return self._size_training 

    @property
    def size_validation(self):
        return self._size_validation

    @property
    def size_testing(self):
        return self._size_testing 

    @property        
    def variables(self):
        return self._variables 

    @property
    def loss_training(self):
        return self._loss_training

    @property
    def loss_testing(self):
        return self._loss_testing

    @property
    def loss_validation(self):
        return self._loss_validation

    @property
    def squared_error_training(self) -> float:
        return self._squared_error_training
    
    @property
    def squared_error_testing(self) -> float:
        return self._squared_error_testing
    
    @property
    def squared_error_validation(self) -> float:
        return self._squared_error_validation

    @property
    def squared_variance_training(self) -> float:
        return self._squared_variance_training

    @property
    def squared_variance_testing(self) -> float:
        return self._squared_variance_testing

    @property
    def squared_variance_validation(self) -> float:
        return self._squared_variance_validation

    @property
    def r_squared_training(self) -> float:
        return self._r_squared_training

    @property
    def r_squared_testing(self) -> float:
        return self._r_squared_testing

    @property
    def r_squared_validation(self) -> float:
        return self._r_squared_validation
        
    @property
    def status(self):
        return self._status

    @property
    def layer_weights(self):
        return self._layer_weights
    
    @property
    def layer_biases(self):
        return self._layer_biases
    
    @property
    def layer_gradients(self):
        return self._layer_gradients

    @property
    def batch_size(self):
        return self._batch_size

    @property
    def layer_outputs(self):
        return self._layer_outputs

    def make_generator_training(self):
        raise NotReplicatedError

    def make_generator_validation(self):
        raise NotReplicatedError        

    def make_generator_testing(self):
        raise NotReplicatedError

    def on_stop(self):
        raise NotReplicatedError        
    
    def on_export(self, path):
        raise NotReplicatedError
    
    @property
    def training_iteration(self):
        return self._training_iteration

    @property
    def validation_iteration(self):
        return self._validation_iteration

    @property
    def testing_iteration(self):
        return self._testing_iteration

    @property
    def progress(self):
        return self._progress

    @property
    def export_modes(self):
        return self._export_modes

class ObjectDetectionLayerReplica(ObjectDetectionLayer):
    def __init__(self, sample, size_training, size_validation, size_testing, variables,
                 accuracy_training, accuracy_testing, accuracy_validation, image_accuracy,
                 loss_training, loss_testing, loss_validation, loss_classification_training, 
                 loss_classification_validation, loss_classification_testing, 
                 loss_bbox_training, loss_bbox_validation, loss_bbox_testing, 
                 grid_size, classes, num_box, num_class, lambdacoord, lambdanoobj,
                 get_predicted_normalized_boxes, get_predicted_classes, get_predicted_objects,
                 status, layer_weights, layer_biases, layer_gradients, layer_outputs,
                 batch_size, training_iteration, validation_iteration,
                 testing_iteration, progress, epoch, export_modes, get_input_data_node, columns):

        self._export_modes = export_modes
        self._epoch = epoch
        self._sample = sample
        self._size_training = size_training
        self._size_validation = size_validation        
        self._size_testing = size_testing
        self._variables = variables
        self._accuracy_training = accuracy_training 
        self._accuracy_validation = accuracy_validation
        self._accuracy_testing = accuracy_testing
        self._image_accuracy = image_accuracy
        self._loss_training = loss_training
        self._loss_validation = loss_validation
        self._loss_testing = loss_testing
        self._classification_loss_training = loss_classification_training
        self._classification_loss_validation = loss_classification_validation
        self._classification_loss_testing = loss_classification_testing
        self._bbox_loss_training = loss_bbox_training
        self._bbox_loss_validation = loss_bbox_validation
        self._bbox_loss_testing = loss_bbox_testing
        self._status = status

        self._grid_size = grid_size
        self._classes = classes
        self._num_box = num_box 
        self._num_class = num_class
        self._lambdacoord = lambdacoord
        self._lambdanoobj = lambdanoobj

        self._input_data_node = get_input_data_node

        self._predicted_normalized_box = get_predicted_normalized_boxes
        self._predicted_class = get_predicted_classes
        self._predicted_object = get_predicted_objects

        self._layer_weights = layer_weights
        self._layer_biases = layer_biases
        self._layer_gradients = layer_gradients
        self._layer_outputs = layer_outputs

        self._batch_size = batch_size
        self._training_iteration = training_iteration
        self._validation_iteration = validation_iteration
        self._testing_iteration = testing_iteration
        self._progress = progress
        self._columns = columns

    @property
    def epoch(self):
        return self._epoch
    
    @property
    def batch_size(self):
        return self._batch_size
    
    @property
    def grid_size(self) -> int:
        return self._grid_size
    
    @property
    def classes(self) -> List[str]:
        return self._classes

    @property
    def num_class(self) -> int:
        return self._num_class

    @property 
    def num_box(self) -> int:
        return self._num_box 

    @property
    def lambdacoord(self) -> float:
        return self._lambdacoord
        
    @property
    def lambdanoobj(self) -> float:  
        return self._lambdanoobj

    @property
    def sample(self):
        return self._sample 

    @property
    def columns(self):
        return self._columns
    
    @property
    def size_training(self):
        return self._size_training 

    @property
    def size_validation(self):
        return self._size_validation

    @property
    def size_testing(self):
        return self._size_testing 

    @property        
    def variables(self):
        return self._variables 

    @property
    def accuracy_training(self):
        return self._accuracy_training

    @property
    def accuracy_testing(self) :
        return self._accuracy_testing

    @property
    def accuracy_validation(self):
        return self._accuracy_validation

    @property
    def image_accuracy(self) -> float:
        return self._image_accuracy

    @property
    def loss_classification_training(self) -> float:
        return self._classification_loss_training        

    @property
    def loss_classification_validation(self) -> float:
        return self._classification_loss_validation        

    @property
    def loss_classification_testing(self) -> float:
        return self._classification_loss_testing

    @property
    def loss_bbox_training(self) -> float:
        return self._bbox_loss_training        

    @property
    def loss_bbox_validation(self) -> float:
        return self._bbox_loss_validation        

    @property
    def loss_bbox_testing(self) -> float:
        return self._bbox_loss_testing

    @property
    def loss_training(self):
        return self._loss_training

    @property
    def get_predicted_normalized_boxes(self):
        return self._predicted_normalized_box

    @property
    def get_predicted_classes(self):
        return self._predicted_class

    @property
    def get_predicted_objects(self):
        return self._predicted_object

    @property
    def loss_testing(self):
        return self._loss_testing

    @property
    def loss_validation(self):
        return self._loss_validation
        
    @property
    def status(self):
        return self._status

    @property
    def layer_weights(self):
        return self._layer_weights
    
    @property
    def layer_biases(self):
        return self._layer_biases
    
    @property
    def layer_gradients(self):
        return self._layer_gradients

    @property
    def layer_outputs(self):
        return self._layer_outputs

    def make_generator_training(self):
        raise NotReplicatedError

    def make_generator_validation(self):
        raise NotReplicatedError        

    def make_generator_testing(self):
        raise NotReplicatedError

    def on_stop(self):
        raise NotReplicatedError        
    
    def on_export(self, path):
        raise NotReplicatedError
    
    @property
    def training_iteration(self):
        return self._training_iteration

    @property
    def validation_iteration(self):
        return self._validation_iteration

    @property
    def testing_iteration(self):
        return self._testing_iteration

    @property
    def progress(self):
        return self._progress

    @property
    def export_modes(self):
        return self._export_modes
    
    @property
    def get_input_data_node(self):
        return self._input_data_node

class RLLayerReplica(RLLayer):
    def __init__(self, sample, variables, action_space,
                 reward, loss_training, loss_testing, loss_validation,
                 n_episodes, episode, gamma, replay_memory_size, transition, 
                 n_steps_max, step_counter, history_length, 
                 status, layer_weights, layer_biases, layer_gradients, layer_outputs,
                 batch_size, progress, n_actions, export_modes):

        self._export_modes = export_modes
        self._action_space = action_space
        self._n_actions = n_actions
        self._episode = episode
        self._n_episodes = n_episodes
        self._reward = reward
        self._gamma = gamma
        self._replay_memory_size = replay_memory_size
        self._transition = transition
        self._n_steps_max = n_steps_max
        self._step_counter = step_counter
        self._history_length = history_length
        self._sample = sample
        self._variables = variables
        self._loss_training = loss_training
        self._loss_validation = loss_validation
        self._loss_testing = loss_testing
        self._status = status
        self._layer_weights = layer_weights
        self._layer_biases = layer_biases
        self._layer_gradients = layer_gradients
        self._layer_outputs = layer_outputs
        self._batch_size = batch_size
        self._progress = progress
    
    @property
    def action_space(self):
        return self._action_space
    
    @property
    def n_actions(self):
        return self._n_actions

    @property
    def episode(self):
        return self._episode

    @property
    def n_episodes(self):
        return self._n_episodes
    
    @property
    def reward(self):
        return self._reward
    
    @property
    def gamma(self):
        return self._gamma
    
    @property
    def replay_memory_size(self):
        return self._replay_memory_size
    
    @property
    def transition(self):
        return self._transition
    
    def make_generator(self):
        raise NotImplementedError

    def reset_environment(self, generator):
        raise NotImplementedError

    def take_action(self, generator, action):
        raise NotImplementedError

    @property
    def n_steps_max(self):
        return self._n_steps_max
    
    @property
    def step_counter(self):
        return self._step_counter
    
    @property
    def history_length(self):
        return self._history_length
    
    @property
    def batch_size(self):
        return self._batch_size
    
    @property
    def sample(self):
        return self._sample 

    @property
    def size_training(self):
        return self._size_training 

    @property
    def size_validation(self):
        return self._size_validation

    @property
    def size_testing(self):
        return self._size_testing 

    @property        
    def variables(self):
        return self._variables 

    @property
    def loss_training(self):
        return self._loss_training

    @property
    def loss_testing(self):
        return self._loss_testing

    @property
    def loss_validation(self):
        return self._loss_validation
        
    @property
    def status(self):
        return self._status

    @property
    def layer_weights(self):
        return self._layer_weights
    
    @property
    def layer_biases(self):
        return self._layer_biases
    
    @property
    def layer_gradients(self):
        return self._layer_gradients

    @property
    def batch_size(self):
        return self._batch_size

    @property
    def layer_outputs(self):
        return self._layer_outputs

    def make_generator_training(self):
        raise NotReplicatedError

    def make_generator_validation(self):
        raise NotReplicatedError        

    def make_generator_testing(self):
        raise NotReplicatedError

    def on_stop(self):
        raise NotReplicatedError        
    
    def on_export(self, path):
        raise NotReplicatedError

    @property
    def progress(self):
        return self._progress

    @property
    def export_modes(self):
        return self._export_modes
    
class GANLayerReplica(GANLayer):
    def __init__(self, sample, size_training, size_validation, size_testing, variables,
                 get_switch_layer_id,
                 generator_loss_training, generator_loss_testing, generator_loss_validation,
                 discriminator_loss_training, discriminator_loss_validation, discriminator_loss_testing,
                 status, layer_weights, layer_biases, layer_gradients, layer_outputs,
                 generator_layer_outputs, real_layer_outputs,
                 batch_size, training_iteration, validation_iteration,
                 testing_iteration, progress, epoch, columns, export_modes):

        self._export_modes = export_modes
        self._epoch = epoch
        self._sample = sample
        self._columns = columns
        self._size_training = size_training
        self._size_validation = size_validation        
        self._size_testing = size_testing
        self._variables = variables
        self._switch_layer_id = get_switch_layer_id
        self._generator_loss_training = generator_loss_training
        self._generator_loss_validation = generator_loss_validation
        self._generator_loss_testing = generator_loss_testing
        self._discriminator_loss_training = discriminator_loss_training
        self._discriminator_loss_validation = discriminator_loss_validation
        self._discriminator_loss_testing = discriminator_loss_testing
        self._status = status

        self._layer_weights = layer_weights
        self._layer_biases = layer_biases
        self._layer_gradients = layer_gradients
        self._layer_outputs = layer_outputs
        self._generator_layer_outputs = generator_layer_outputs
        self._real_layer_outputs = real_layer_outputs

        self._batch_size = batch_size
        self._training_iteration = training_iteration
        self._validation_iteration = validation_iteration
        self._testing_iteration = testing_iteration
        self._progress = progress

    @property
    def epoch(self):
        return self._epoch
    
    @property
    def batch_size(self):
        return self._batch_size
    
    @property
    def sample(self):
        return self._sample 

    @property
    def columns(self):
        return self._columns

    @property
    def size_training(self):
        return self._size_training 

    @property
    def size_validation(self):
        return self._size_validation

    @property
    def size_testing(self):
        return self._size_testing 

    @property        
    def variables(self):
        return self._variables 

    @property
    def get_switch_layer_id(self):
        return self._switch_layer_id

    @property
    def generator_loss_training(self):
        return self._generator_loss_training

    @property
    def generator_loss_testing(self):
        return self._generator_loss_testing

    @property
    def generator_loss_validation(self):
        return self._generator_loss_validation

    @property
    def discriminator_loss_training(self):
        return self._discriminator_loss_training

    @property
    def discriminator_loss_testing(self):
        return self._discriminator_loss_testing

    @property
    def discriminator_loss_validation(self):
        return self._discriminator_loss_validation
        
    @property
    def status(self):
        return self._status

    @property
    def layer_weights(self):
        return self._layer_weights
    
    @property
    def layer_biases(self):
        return self._layer_biases
    
    @property
    def layer_gradients(self):
        return self._layer_gradients

    @property
    def batch_size(self):
        return self._batch_size

    @property
    def layer_outputs(self):
        return self._layer_outputs

    @property
    def generator_layer_outputs(self):
        return self._generator_layer_outputs

    @property
    def real_layer_outputs(self):
        return self._real_layer_outputs

    def make_generator_training(self):
        raise NotReplicatedError

    def make_generator_validation(self):
        raise NotReplicatedError        

    def make_generator_testing(self):
        raise NotReplicatedError

    def on_stop(self):
        raise NotReplicatedError        
    
    def on_export(self, path):
        raise NotReplicatedError
    
    @property
    def training_iteration(self):
        return self._training_iteration

    @property
    def validation_iteration(self):
        return self._validation_iteration

    @property
    def testing_iteration(self):
        return self._testing_iteration

    @property
    def progress(self):
        return self._progress

    @property
    def export_modes(self):
        return self._export_modes


class InnerLayerReplica(InnerLayer):
    def __init__(self, variables):
        self._variables = variables

    @property        
    def variables(self):
        return self._variables

    def __call__(self, x):
        raise NotReplicatedError        
    
    
class Tf1xLayerReplica(Tf1xLayer):
    def __init__(self, variables):
        self._variables = variables

    @property        
    def variables(self):
        return self._variables

    @property        
    def trainable_variables(self):
        raise NotReplicatedError        
    
    def get_sample(self, sess=None):
        raise NotReplicatedError
    
    @property        
    def weights(self):
        raise NotReplicatedError        
    
    @property        
    def biases(self):
        raise NotReplicatedError        
    
    def __call__(self, x: tf.Tensor):
        raise NotReplicatedError        

    def __call__(self, x: List[tf.Tensor]):
        raise NotReplicatedError
