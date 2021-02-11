import tensorflow as tf
import collections
import numpy as np

from perceptilabs.trainer.model import TrainingModel


class Trainer:
    def __init__(self, script_factory, data_loader, graph_spec):
        self._script_factory = script_factory
        self._data_loader = data_loader
        self._graph_spec = graph_spec
        
        self._headless = False

        self._num_epochs_completed = 0        
        self._num_epochs = 10 # TODO: read from spec (story 1535)
        self._batch_size = 2 # TODO: read from spec (story 1535)

        self._reset_tracked_tensors()
        self._initialize_batch_counters(data_loader)        
        self._set_status('Waiting')
        
    def run(self, _=None, on_iterate=None, model_id=None):
        """ Run all training steps """
        # TODO: remove _, on_iterate and model_id when possible
        for _ in self.run_stepwise():
            pass
    
    def run_stepwise(self):
        """ Take a training/validation step and yield """        
        self._training_model = TrainingModel(self._script_factory, self._graph_spec)
        dataset_train = self._data_loader.get_dataset().batch(self.batch_size)
        
        self._metric_training_loss = tf.keras.metrics.Mean()
        self._metric_training_accuracy = tf.keras.metrics.CategoricalAccuracy()
        self._metric_training_auc = tf.keras.metrics.AUC(curve='ROC')
        
        self._metric_validation_loss = tf.keras.metrics.Mean()
        self._metric_validation_accuracy = tf.keras.metrics.CategoricalAccuracy()
        self._metric_validation_auc = tf.keras.metrics.AUC(curve='ROC')

        # TODO: Implement different optimizers (story 1535)
        optimizer = tf.keras.optimizers.SGD(learning_rate=0.1) #  TODO: fix learning rate (story 1535)

        losses = {
            layer_spec.feature_name: tf.keras.losses.MeanSquaredError() # TODO: get from training settings/output layers (story 1536)
            for layer_spec in self._graph_spec.layers
            if layer_spec.is_output_layer
        }

        self._num_epochs_completed = 0
        while self._num_epochs_completed < self.num_epochs:
            self._set_status('Training')
            yield from self._loop_over_dataset(
                self._training_model,
                losses,
                dataset_train,
                self._metric_training_loss,
                self._metric_training_accuracy,
                self._metric_training_auc,
                self._set_num_training_batches_completed_this_epoch,
                training=True,
                optimizer=optimizer
            )
            self._set_status('Validation')
            yield # TODO: loop over dataset for validation (story 1537)
             
            self._num_epochs_completed += 1
            yield
            
        self._set_status('Finished')
        # TODO: automatic export at end of training (story 1538)

    def _loop_over_dataset(self, model, losses, dataset, metric_loss, metric_accuracy, metric_auc, set_num_batches_completed_this_epoch, training=True, optimizer=None):
        """ Loop over all batches of data once """
        metric_loss.reset_states()
        metric_accuracy.reset_states()
        metric_auc.reset_states()

        for step, (inputs_batch, targets_batch) in enumerate(dataset):
            weights_by_layer, biases_by_layer, gradients_by_layer, final_and_intermediate_outputs_by_layer = self._work_on_batch(
                model, losses, inputs_batch, targets_batch, metric_loss, training, optimizer
            )
            if self._headless:
                self._reset_tracked_tensors()
            else:
                self._update_tracked_tensors(weights_by_layer, biases_by_layer, gradients_by_layer, final_and_intermediate_outputs_by_layer)
            
            self._num_batches_completed_all_epochs += 1
            set_num_batches_completed_this_epoch(step + 1)            
            yield

    @tf.function
    def _work_on_batch(self, model, losses, inputs_batch, targets_batch, metric_loss, training, optimizer):
        """ Train or validate on a batch of data """
        with tf.GradientTape() as tape:
            predictions_batch, final_and_intermediate_outputs = model(inputs_batch, training=training)
            total_loss = self._compute_total_loss(predictions_batch, targets_batch, losses)
            
        metric_loss.update_state(total_loss)
        # TODO: implement accuracy metric (story 1540)
        # TODO: implement auc metric (story 1541)

        trainables_by_layer, weights_by_layer, biases_by_layer = self._collect_trainables_by_layer(model)
        gradients_by_layer, grads_and_vars = self._compute_gradients(tape, total_loss, trainables_by_layer, model.trainable_variables)
        
        if training:
            optimizer.apply_gradients(grads_and_vars)

        return weights_by_layer, biases_by_layer, gradients_by_layer, final_and_intermediate_outputs

    def _compute_gradients(self, tape, total_loss, trainables_by_layer, flat_trainables):
        """ Compute the gradients. Return two variations, one structured by layer and one flat """
        gradients_by_layer, flat_gradients = tape.gradient(total_loss, (trainables_by_layer, flat_trainables))
        grads_and_vars = zip(flat_gradients, flat_trainables)
        return gradients_by_layer, grads_and_vars    

    def _compute_total_loss(self, predictions_batch, targets_batch, losses):
        """ Compute the combined loss of all output layers """
        total_loss = tf.constant(0.0)
        for output_name, loss_fn in losses.items():
            # TODO: weight the different losses (story 1542)
            total_loss += loss_fn(
                predictions_batch[output_name],
                tf.reshape(targets_batch[output_name], shape=predictions_batch[output_name].shape)
            )
        return total_loss

    def _reset_tracked_tensors(self):
        self._update_tracked_tensors({}, {}, {}, {})

    def _update_tracked_tensors(self, weights_by_layer, biases_by_layer, gradients_by_layer, final_and_intermediate_outputs_by_layer):
        """ Take a snapshot of the current tensors (e.g., layer weights) """
        self._layer_gradients = gradients_by_layer
        self._layer_outputs = final_and_intermediate_outputs_by_layer
        self._layer_weights = weights_by_layer
        self._layer_biases = biases_by_layer

    def _collect_trainables_by_layer(self, model):
        """ Collect the trainable tensors from the model and structure them by layer """
        trainables_by_layer, weights_by_layer, biases_by_layer = {}, {}, {}
        for layer_id, layer in model.layers_by_id.items():
            weights, biases = getattr(layer, 'visualized_trainables', ({}, {})) # TODO: check isinstance(..., PerceptiLabsVisualizer) once story 1534 has been completed
            weights_by_layer[layer_id] = weights
            biases_by_layer[layer_id] = biases

            trainables_by_layer[layer_id] = {}
            trainables_by_layer[layer_id].update(weights_by_layer[layer_id])
            trainables_by_layer[layer_id].update(biases_by_layer[layer_id])
            
        return trainables_by_layer, weights_by_layer, biases_by_layer

    def _set_num_training_batches_completed_this_epoch(self, value):
        """ The number of iterations completed in the _current_ epoch """
        self._num_training_batches_completed_this_epoch = value

    def _set_num_validation_batches_completed_this_epoch(self, value):
        """ The number of iterations completed in the _current_ epoch """        
        self._num_validation_batches_completed_this_epoch = value

    def _set_status(self, value):
        if value not in ['Waiting', 'Training', 'Validation', 'Finished']:
            raise ValueError(f"Cannot set status to '{value}'")
        self._status = value

    @property
    def status(self):
        """ The current training status """
        return self._status
        
    @property
    def layer_weights(self):
        """The weight values of each layer in the input Graph during the training.

        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain weight name and value pairs. 
        """        
        return self._evaluate_nested_tensors(self._layer_weights)

    @property
    def layer_biases(self):
        """The bias values of each layer in the input Graph during the training.

        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain weight name and value pairs. 
        """
        return self._evaluate_nested_tensors(self._layer_biases)        
    
    @property
    def layer_gradients(self):
        """The gradients with respect to the loss of all trainable variables of each layer in the input Graph.

        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain gradient name and value pairs.
        """        
        return self._evaluate_nested_tensors(self._layer_gradients)
    
    @property
    def layer_outputs(self):
        """The output values of each layer in the input Graph during the training (e.g., tf.Tensors evaluated for each iteration)

        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain variable name and value pairs.
        """
        return self._evaluate_nested_tensors(self._layer_outputs)

    @property
    def batch_size(self):
        return self._batch_size

    @property
    def num_epochs(self):
        return self._num_epochs

    @property
    def num_epochs_completed(self):
        return self._num_epochs_completed

    @property
    def num_batches_completed_all_epochs(self):
        return self._num_batches_completed_all_epochs

    @property
    def num_batches_all_epochs(self):
        return self._num_batches_all_epochs

    @property
    def num_batches_per_epoch(self):
        return self._num_batches_per_epoch

    @property
    def num_batches_completed_this_epoch(self):
        return self.num_training_batches_completed_this_epoch + self.num_validation_batches_completed_this_epoch
    @property
    def num_training_batches_completed_this_epoch(self):
        return self._num_training_batches_completed_this_epoch

    @property
    def num_validation_batches_completed_this_epoch(self):
        return self._num_validation_batches_completed_this_epoch

    def _initialize_batch_counters(self, data_loader):
        """ Initialize iteration/batch counters to keep track of progress """
        dataset_size = len(list(data_loader.get_dataset()))

        self._num_batches_per_epoch = int(np.ceil(dataset_size / self.batch_size))
        self._num_batches_all_epochs = self._num_batches_per_epoch * self._num_epochs
        self._num_batches_completed_all_epochs = 0

        self._set_num_training_batches_completed_this_epoch(0)
        self._set_num_validation_batches_completed_this_epoch(0)

    @property
    def progress(self) -> float:
        return self.num_batches_completed_all_epochs / self.num_batches_all_epochs

    @property
    def is_closed(self):
        return self.status == 'Finished'

    @property
    def is_ready(self):
        return True

    @property
    def is_paused(self):
        # TODO: implement (story 1543)
        return False

    def pause(self):
        # TODO: implement (story 1543)
        pass

    def unpause(self):
        # TODO: implement (story 1543)
        pass
    
    def stop(self):
        # TODO: implement (story 1544)
        pass
    
    def headless_on(self):
        # TODO: implement (story 1545)
        pass
    
    def headless_off(self):
        # TODO: implement (story 1545)
        pass        

    def export(self, path, mode):
        # TODO: implement (1538)
        if mode == 'TFModel':
            self.save_model(path)

    def close(self):
        self.stop()
        
    def save_model(self, path):
        """ Save the model """
        model = self.get_inference_model()
        model.save(path)

    def get_inference_model(self):
        """ Convert the Training Model to a simpler version (e.g., skip intermediate outputs)  """        
        # TODO: add option to include pre- and post-processing pipelines (story 1609)
        inputs = {}
        for layer_spec in self._graph_spec:
            if not layer_spec.is_input_layer:
                continue
            shape = self._data_loader.get_feature_shape(layer_spec.feature_name)
            inputs[layer_spec.feature_name] = tf.keras.Input(shape=shape)
                
        outputs, _ = self._training_model(inputs)
        inference_model = tf.keras.Model(inputs=inputs, outputs=outputs)
        return inference_model        

    def _evaluate_nested_tensors(self, outer_dict):
        """ Evaluate tensors in a nested dictionary """
        new_outer = {}
        for layer_id, inner_dict in outer_dict.items():
            new_outer[layer_id] = {}

            for tensor_name, tensor in inner_dict.items():
                new_outer[layer_id][tensor_name] = tensor.numpy()
                    
        return new_outer
    
    def _get_train_dict(self):
        dict_ = {}
        for layer_spec in self._graph_spec.layers:
            # TODO: implement accuracy (story 1540)
            # TODO: implement auc metric (story 1541)
            # TODO: implement loss (
            dict_[layer_spec.id_] = {
                'X': {'input1': {'Y': 123}}, # TODO: fix (story 1562)
                'Y': 123, # TODO: fix Y (story 1562)
                'W': 1234, # TODO: fix W (story 1562)
                'Biases': 400, # TODO: fix biases (story 1562)
                'Gradient': { # TODO: fix gradients (story 1562)
                    'Min': [0.3, 0.4, 0.5], 
                    'Max': [0.8, 0.9, 0.10],
                    'Average': [0.5, 0.6, 0.8]
                }
            }
        return dict_

    def get_results(self):
        """ Return a dict for the coreInterface to derive plots from """
        dict_ = {
            'iter': self.num_batches_completed_this_epoch,
            'maxIter': self.num_batches_per_epoch,
            'epoch': self.num_epochs_completed,
            'maxEpochs': self.num_epochs,
            'batch_size': self.batch_size,
            'trainingIterations': self.num_training_batches_completed_this_epoch,
            'trainDict': self._get_train_dict(),
            'trainingStatus': self.status,
            'progress': self.progress, 
            'status': 'Paused' if self.is_paused else 'Running',
            'training_duration': 5.0 # TODO: fix training duration (story 1569)             
        }
        return dict_


        
        
        
