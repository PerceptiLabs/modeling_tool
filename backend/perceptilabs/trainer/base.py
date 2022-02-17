import collections
import os
import sys
import time
import logging
from typing import Dict

import tensorflow as tf
import tensorflow.keras.backend as K
import numpy as np
import json
import time
import logging

from perceptilabs.layers.visualizer import PerceptiLabsVisualizer
from perceptilabs.trainer.model import TrainingModel
from perceptilabs.stats import SampleStatsTracker, SampleStats, GradientStatsTracker, GradientStats, GlobalStatsTracker, TrainingStatsTracker
from perceptilabs.layers.iooutput.stats import ImageOutputStatsTracker, NumericalOutputStatsTracker, CategoricalOutputStatsTracker, MaskOutputStatsTracker
from perceptilabs.layers.inner_layer_stats import InnerLayersStatsTracker
from perceptilabs.layers.ioinput.stats import InputStatsTracker


from perceptilabs.trainer.losses import weighted_crossentropy, dice
from perceptilabs.utils import get_memory_usage, sanitize_path
from perceptilabs.hardware import HardwareStats
import perceptilabs.tracking as tracking
import perceptilabs.utils as utils
import perceptilabs.settings as settings


logger = logging.getLogger(__name__)


class Trainer:
    def __init__(self, data_loader, training_model, training_settings, training_session_id, model_id=None, initial_state=None, on_training_started=None, on_training_stopped=None, on_training_completed=None, on_epoch_completed=None):
        self._on_training_started = on_training_started
        self._on_training_stopped = on_training_stopped
        self._on_training_completed = on_training_completed
        self._on_epoch_completed = on_epoch_completed

        self._initial_state = initial_state
        self._training_settings = training_settings.copy()

        self._hardware_stats = HardwareStats(
            refresh_interval=settings.TRAINING_RESULTS_REFRESH_INTERVAL)  # Worst case scenario, it is a factor of 2 seconds behind.

        self._model_id = model_id

        self._data_loader = data_loader
        self._training_model = training_model
        self._graph_spec = training_model.graph_spec

        self._optimizer = self._resolve_optimizer(self._training_settings)
        self._loss_functions = self._setup_loss_functions(self._training_settings)

        self._training_session_id = training_session_id
        self._auto_checkpoint = training_settings.get('AutoCheckpoint', False)

        self._initialize_results()
        self._data_initialized = False

    def _initialize_results(self):
        self._batch_size = int(self._training_settings['Batch_size'])
        self._shuffle_training_set = self._training_settings['Shuffle']
        self._headless = False

        self._num_batches_per_epoch = -1  # Not known until data loader is ran
        self._num_batches_all_epochs = -1  # Not known until data loader is ran

        if self._initial_state is None:
            self._set_status('Waiting')
            self._training_time = 0.0
            self._num_epochs_completed = 0
            self._num_batches_completed_all_epochs = 0
            self._set_num_training_batches_completed_this_epoch(0)
            self._set_num_validation_batches_completed_this_epoch(0)
            self._num_epochs = int(self._training_settings['Epochs'])
        else:
            initial_state = self._initial_state
            self._set_status(self._initial_state['status'])
            self._training_time = initial_state['training_time']
            self._num_epochs_completed = initial_state['num_epochs_completed']
            self._num_batches_completed_all_epochs = initial_state['num_batches_completed_all_epochs']
            self._set_num_training_batches_completed_this_epoch(
                initial_state['num_training_batches_completed_this_epoch'])
            self._set_num_validation_batches_completed_this_epoch(
                initial_state['num_validation_batches_completed_this_epoch'])
            self._num_epochs = int(self._training_settings['Epochs']) + initial_state['num_epochs_completed']
        self._reset_tracked_values(self._initial_state)

    def ensure_data_initialized(self):
        if self._data_initialized:
            return

        self._data_loader.ensure_initialized()
        training_size = self._data_loader.get_dataset_size(partition='training')
        validation_size = self._data_loader.get_dataset_size(partition='validation')

        training_batches_per_epoch = int(np.ceil(training_size / self._batch_size))
        validation_batches_per_epoch = int(np.ceil(validation_size / self._batch_size))

        self._num_batches_per_epoch = training_batches_per_epoch + validation_batches_per_epoch
        self._num_batches_all_epochs = self._num_batches_per_epoch * self._num_epochs
        self._data_initialized = True

    def save_state(self):
        state = {
            'cpu_usage': self._cpu_usage,
            'gpu_usage': self._gpu_usage,
            'mem_usage': self._mem_usage,
            'status': self._status,
            'training_time': self._training_time,
            'num_epochs_completed': self._num_epochs_completed,
            'num_batches_completed_all_epochs': self._num_batches_completed_all_epochs,
            'num_training_batches_completed_this_epoch': self._num_training_batches_completed_this_epoch,
            'num_validation_batches_completed_this_epoch': self._num_validation_batches_completed_this_epoch,
            'global_stats_tracker': self._global_stats_tracker,
            'input_stats_tracker': self._input_stats_tracker,
            'prediction_stats_tracker': self._prediction_stats_tracker,
            'target_stats_tracker': self._target_stats_tracker,
            'output_trackers': {
                layer_id: tracker
                for layer_id, tracker in self._output_trackers.items()
            },
            'input_trackers': {
                layer_id: tracker
                for layer_id, tracker in self._input_trackers.items()
            },
            'inner_layers_stats_tracker': self._inner_layers_stats_tracker
        }
        return state

    def validate(self):
        """ Compute the loss. If the model or data is faulty, we get a crash.

        Should be seen as a final error check
        """
        dataset = self._data_loader.get_dataset().batch(1)
        inputs_batch, targets_batch = next(iter(dataset))

        predictions_batch, final_and_intermediate_outputs = self._training_model(
            inputs_batch, training=False)
        self._compute_total_loss(
            predictions_batch, targets_batch, self._loss_functions)

    def run(self, _=None, on_iterate=None, model_id=None):
        """ Run all training steps """
        # TODO: remove _, on_iterate and model_id when possible
        for _ in self.run_stepwise():
            pass

    def run_stepwise(self):
        """ Take a training/validation step and yield """
        self.ensure_data_initialized()
        peak_memory_usage = get_memory_usage()

        if self._num_epochs_completed == 0:
            logger.info("Entering training loop")
        else:
            logger.info(f"Entering training loop (starting from epoch {self._num_epochs_completed}/{self.num_epochs})")

        if self._on_training_started:
            self._on_training_started()

        self._set_status('Training')
        self._log_model_summary()

        while self._num_epochs_completed < self.num_epochs and not self.is_closed:
            t0 = time.perf_counter()
            yield from self._sleep_while_paused()
            if self.is_closed:
                break

            self._set_status('Training')

            yield from self._loop_over_dataset(
                self._training_model,
                self._loss_functions,
                self._get_training_set(),
                self._set_num_training_batches_completed_this_epoch,
                self.is_closed,
                is_training=True,
                optimizer=self._optimizer
            )

            yield from self._sleep_while_paused()
            if self.is_closed:
                break

            self._set_status('Validation')

            yield from self._loop_over_dataset(
                self._training_model,
                self._loss_functions,
                self._get_validation_set(),
                self._set_num_validation_batches_completed_this_epoch,
                self.is_closed,
                is_training=False
            )

            if self.is_closed:
                break

            epoch_time = time.perf_counter() - t0

            if self._on_epoch_completed:
                self._on_epoch_completed(self._num_epochs_completed, self, epoch_time)

            self._num_epochs_completed += 1
            self._log_epoch_summary(epoch_time)
            self._training_time += epoch_time

            current_memory_usage = get_memory_usage()
            if current_memory_usage > peak_memory_usage:
                peak_memory_usage = current_memory_usage

            yield

        if self._num_epochs_completed == self.num_epochs:
            self._set_status('Finished')

        logger.info(
            f"Training completed. Total duration: {round(self._training_time, 3)} s")

        if self._on_training_completed:
            dataset_size, sample_size, num_iters_completed, data_units_iter_based, \
                data_units_epoch_based, model_params, trainable_params = self._get_mixpanel_pricing_metrics()
            self._on_training_completed(
                self,
                self._training_time,
                dataset_size,
                sample_size,
                num_iters_completed,
                self.num_epochs_completed,
                self.batch_size,
                data_units_iter_based,
                data_units_epoch_based,
                model_params,
                trainable_params,
                peak_memory_usage,
                self.get_output_stats_summaries()
            )
        else:
            logger.info(
                f"Training ended before completion. Total duration: {round(self._training_time, 3)} s")

    def _log_model_summary(self):
        try:
            batch, _ = self._data_loader.get_example_batch(batch_size=1)
        except ValueError:
            logger.exception(
                f"The model summary failed because the data loader couldn't get an example batch!"
                f"This is usually because the data loader isn't instantiated properly."
            )
            return

        _ = self._training_model(batch)
        logger.info(self._training_model.summary())

    def _log_epoch_summary(self, epoch_time):
        logger.info(
            f"Finished epoch {self._num_epochs_completed}/{self.num_epochs} - "
            f"Epoch duration: {round(epoch_time, 3)} s - "
            f"Num training (validation) batches completed : {self.num_training_batches_completed_this_epoch} ({self.num_validation_batches_completed_this_epoch})"
        )

    def _loop_over_dataset(self, model, loss_functions, dataset, set_num_batches_completed_this_epoch, is_closed, is_training=True, optimizer=None):
        """ Loop over all batches of data once """
        for steps_completed, (inputs_batch, targets_batch) in enumerate(dataset):
            if is_closed:
                break
            else:
                predictions_batch, trainables_by_layer, gradients_by_layer, final_and_intermediate_outputs_by_layer, \
                    total_loss, individual_losses = self._work_on_batch(
                        model, loss_functions, inputs_batch, targets_batch, is_training, optimizer
                    )

                if self._headless:
                    self._reset_tracked_values()
                else:
                    self._update_tracked_values(
                        trainables_by_layer,
                        gradients_by_layer,
                        final_and_intermediate_outputs_by_layer,
                        inputs_batch,
                        predictions_batch,
                        targets_batch,
                        total_loss,
                        individual_losses,
                        is_training,
                        steps_completed
                    )

                self._num_batches_completed_all_epochs += 1
                set_num_batches_completed_this_epoch(steps_completed + 1)
                yield

    @tf.function
    def _work_on_batch(self, model, loss_functions, inputs_batch, targets_batch, is_training, optimizer):
        """ Train or validate on a batch of data """
        with tf.GradientTape() as tape:
            predictions_batch, final_and_intermediate_outputs = model(
                inputs_batch, training=is_training)
            total_loss, individual_losses = self._compute_total_loss(
                predictions_batch, targets_batch, loss_functions)

        trainables_by_layer = self._collect_trainables_by_layer(model)
        gradients_by_layer, grads_and_vars = self._compute_gradients(
            tape, total_loss, trainables_by_layer, model.trainable_variables)

        if is_training:
            optimizer.apply_gradients(grads_and_vars)

        return predictions_batch, trainables_by_layer, gradients_by_layer, final_and_intermediate_outputs, total_loss, individual_losses

    def _compute_gradients(self, tape, total_loss, trainables_by_layer, flat_trainables):
        """ Compute the gradients. Return two variations, one structured by layer and one flat """
        gradients_by_layer, flat_gradients = tape.gradient(
            total_loss, (trainables_by_layer, flat_trainables))
        grads_and_vars = zip(flat_gradients, flat_trainables)
        return gradients_by_layer, grads_and_vars

    def _compute_total_loss(self, predictions_batch, targets_batch, losses):
        """ Compute the combined loss of all output layers """
        total_loss = tf.constant(0.0)
        individual_losses = {}

        for feature_name, loss_fn in losses.items():
            # TODO: weight the different losses (story 1542)

            individual_losses[feature_name] = loss_fn(
                tf.reshape(targets_batch[feature_name],
                           shape=predictions_batch[feature_name].shape),
                predictions_batch[feature_name]
            )
            total_loss += individual_losses[feature_name]

        return total_loss, individual_losses

    def _reset_tracked_values(self, initial_state=None):
        if initial_state is None:
            self._global_stats_tracker = GlobalStatsTracker()
            self._input_stats_tracker = SampleStatsTracker()
            self._prediction_stats_tracker = SampleStatsTracker()
            self._target_stats_tracker = SampleStatsTracker()
            inner_layers = self._get_inner_layer_ids_and_types()
            self._inner_layers_stats_tracker = InnerLayersStatsTracker(inner_layers)

            self._cpu_usage = self._hardware_stats.cpu_usage
            self._gpu_usage = self._hardware_stats.gpu_usage
            self._mem_usage = self._hardware_stats.mem_usage
        else:
            self._global_stats_tracker = initial_state['global_stats_tracker']
            self._input_stats_tracker = initial_state['input_stats_tracker']
            self._prediction_stats_tracker = initial_state['prediction_stats_tracker']
            self._target_stats_tracker = initial_state['target_stats_tracker']
            self._inner_layers_stats_tracker = initial_state['inner_layers_stats_tracker']

            self._cpu_usage = initial_state['cpu_usage']
            self._gpu_usage = initial_state['gpu_usage']
            self._mem_usage = initial_state['mem_usage']

        self._input_trackers = {}
        for layer_spec in self._graph_spec.input_layers:
            if initial_state is None:
                self._input_trackers[layer_spec.id_] = InputStatsTracker()
            else:
                self._input_trackers[layer_spec.id_] = initial_state['input_trackers'][layer_spec.id_]

        self._output_trackers = {}
        for layer_spec in self._graph_spec.target_layers:
            if initial_state is None:
                self._output_trackers[layer_spec.id_] = self._get_output_stats_tracker(layer_spec.datatype, layer_spec.feature_name)
            else:
                self._output_trackers[layer_spec.id_] = initial_state['output_trackers'][layer_spec.id_]

    def _get_inner_layer_ids_and_types(self):
        inner_layers = {}
        for layer_spec in self._graph_spec.inner_layers:
            inner_layers[layer_spec.id_] = layer_spec.type_
        return inner_layers

    def _get_output_stats_tracker(self, datatype, feature_name):
        if datatype == 'numerical':
            return NumericalOutputStatsTracker()
        elif datatype == 'categorical':
            return CategoricalOutputStatsTracker()
        elif datatype == 'binary':
            return CategoricalOutputStatsTracker()
        elif datatype == 'image':
            return ImageOutputStatsTracker()
        elif datatype == 'mask':
            return MaskOutputStatsTracker()

    def _update_tracked_values(
            self, trainables_by_layer, gradients_by_layer, final_and_intermediate_outputs_by_layer,
            inputs_batch, predictions_batch, targets_batch,
            total_loss, individual_losses, is_training, steps_completed
    ):
        """ Take a snapshot of the current tensors (e.g., layer weights) """
        self._cpu_usage = self._hardware_stats.cpu_usage
        self._gpu_usage = self._hardware_stats.gpu_usage
        self._mem_usage = self._hardware_stats.mem_usage

        self._inner_layers_stats_tracker.update(
            outputs=final_and_intermediate_outputs_by_layer,
            trainables_by_layer=trainables_by_layer,
            gradients_by_layer=gradients_by_layer)

        self._global_stats_tracker.update(
            loss=total_loss,
            epochs_completed=self._num_epochs_completed,
            steps_completed=steps_completed,
            is_training=is_training
        )

        id_to_feature = {
            layer_spec.id_: layer_spec.feature_name
            for layer_spec in self._graph_spec.io_layers
        }

        self._input_stats_tracker.update(id_to_feature=id_to_feature, sample_batch=inputs_batch)
        self._prediction_stats_tracker.update(id_to_feature=id_to_feature, sample_batch=predictions_batch)
        self._target_stats_tracker.update(id_to_feature=id_to_feature, sample_batch=targets_batch)

        for layer_spec in self._graph_spec.input_layers:
            tracker = self._input_trackers[layer_spec.id_]
            tracker.update(inputs_batch=inputs_batch[layer_spec.feature_name])

        for layer_spec in self._graph_spec.target_layers:
            tracker = self._output_trackers[layer_spec.id_]
            postprocessing = self._data_loader.get_postprocessing_pipeline(
                layer_spec.feature_name)

            tracker.update(
                inputs_batch=inputs_batch,
                predictions_batch=predictions_batch[layer_spec.feature_name],
                targets_batch=targets_batch[layer_spec.feature_name],
                epochs_completed=self._num_epochs_completed,
                loss=individual_losses[layer_spec.feature_name],
                postprocessing=postprocessing,
                steps_completed=steps_completed,
                is_training=is_training
            )

    def _collect_trainables_by_layer(self, model):
        """ Collect the trainable tensors from the model and structure them by layer """
        trainables_by_layer = {}
        for layer_id, layer in model.layers_by_id.items():
            if isinstance(layer, PerceptiLabsVisualizer):
                weights, bias = layer.visualized_trainables

                trainables = {}
                if isinstance(weights, tf.Variable):
                    trainables['weights'] = weights
                elif isinstance(weights, list):
                    trainables['weights'] = weights[0]
                if isinstance(bias, tf.Variable):
                    trainables['bias'] = bias

                if trainables:
                    trainables_by_layer[layer_id] = trainables

            elif len(layer.trainable_variables) > 0:
                logger.warning(
                    "Layer {layer_id} has trainable variables but does not implement the PerceptiLabsVisualizer abstract class. Weights, biases and derived quantities such as gradients will not be visualized correctly.")

        return trainables_by_layer

    def _set_num_training_batches_completed_this_epoch(self, value):
        """ The number of iterations completed in the _current_ epoch """
        self._num_training_batches_completed_this_epoch = value

    def _set_num_validation_batches_completed_this_epoch(self, value):
        """ The number of iterations completed in the _current_ epoch """
        self._num_validation_batches_completed_this_epoch = value

    def _set_status(self, value):
        if value not in ['Waiting', 'Paused', 'Training', 'Validation', 'Finished', 'Stopped']:
            raise ValueError(f"Cannot set status to '{value}'")
        self._status = value

    def _get_mixpanel_pricing_metrics(self):
            sample_size = sys.getsizeof(self._data_loader.get_sample(partition='training'))

            training_size = self._data_loader.get_dataset_size(partition='training')
            validation_size = self._data_loader.get_dataset_size(partition='validation')
            test_size = self._data_loader.get_dataset_size(partition='test')

            dataset_size = training_size + validation_size + test_size

            num_iters_completed = self._num_batches_completed_all_epochs
            data_units_iter_based = sample_size * num_iters_completed * self._batch_size
            data_units_epoch_based = sample_size * dataset_size * self._num_epochs_completed

            model_params = self._training_model.count_params()
            trainable_params = int(np.sum([K.count_params(w) for w in self._training_model.trainable_weights]))

            return dataset_size, sample_size, num_iters_completed, data_units_iter_based,\
                data_units_epoch_based, model_params, trainable_params

    @property
    def auto_checkpoint(self):
        return self._auto_checkpoint

    @property
    def status(self):
        """ The current training status """
        return self._status

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
        """ The number of batches completed is equivelant to the number of iterations completed
            as it refers to the number of batches that have completed a forward/backward pass.
            We call it a "batch" in this context because 'iterations' is a bit ambiguous in larger
            software settings.
        """
        return self._num_batches_completed_all_epochs

    @property
    def num_batches_all_epochs(self):
        return self._num_batches_all_epochs

    @property
    def num_batches_per_epoch(self):
        return self._num_batches_per_epoch

    @property
    def num_batches_completed_this_epoch(self):
        """ The number of batches completed is equivelant to the number of iterations completed
            as it refers to the number of batches that have completed a forward/backward pass.
            We call it a "batch" in this context because 'iterations' is a bit ambiguous in larger
            software settings.
        """
        return self.num_training_batches_completed_this_epoch + self.num_validation_batches_completed_this_epoch

    @property
    def num_training_batches_completed_this_epoch(self):
        return self._num_training_batches_completed_this_epoch

    @property
    def num_validation_batches_completed_this_epoch(self):
        return self._num_validation_batches_completed_this_epoch

    @property
    def progress(self) -> float:
        return self.num_batches_completed_all_epochs / self.num_batches_all_epochs

    @property
    def is_closed(self):
        return self.status == 'Finished' or self.status == 'Stopped'

    @property
    def is_ready(self):
        return True

    @property
    def is_paused(self):
        return self.status == 'Paused'

    def _sleep_while_paused(self):
        while self.is_paused:
            time.sleep(0.1)
            yield

    def _store_prev_status(self):
        if self.status == 'Training':
            self._prev_status = 'Training'
        if self.status == 'Validation':
            self._prev_status = 'Validation'

    def pause(self):
        self._store_prev_status()
        self._set_status('Paused')
        logger.info(f"Trainer is in state Paused")

    def unpause(self):
        self._set_status(self._prev_status)
        logger.info(f"Trainer is in state %s", self._prev_status)

    def stop(self):
        self._set_status('Stopped')

        if self._on_training_stopped:
            dataset_size, sample_size, num_iters_completed, data_units_iter_based, \
                data_units_epoch_based, model_params, trainable_params = self._get_mixpanel_pricing_metrics()

            self._on_training_stopped(
                self._training_time,
                dataset_size,
                sample_size,
                num_iters_completed,
                self.num_epochs_completed,
                self.batch_size,
                data_units_iter_based,
                data_units_epoch_based,
                model_params,
                trainable_params,
                self.progress,
                self.get_output_stats_summaries()
            )

    def headless_on(self):
        # TODO: implement (story 1545)
        pass

    def headless_off(self):
        # TODO: implement (story 1545)
        pass

    def close(self):
        self.stop()

    def get_results(self):
        """ Return a dict for to derive plots from """
        t0 = time.perf_counter()
        dict_ = {
            'iter': self.num_batches_completed_this_epoch,
            'maxIter': self.num_batches_per_epoch,
            'epoch': self.num_epochs_completed,
            'maxEpochs': self.num_epochs,
            'batch_size': self.batch_size,
            'trainingIterations': self.num_training_batches_completed_this_epoch,
            'trainingStatus': 'Paused' if self.is_paused else self.status,
            'progress': self.progress,
            'status': 'Paused' if self.is_paused else 'Running',
            'training_duration': self._training_time,
            'global_stats': self.get_global_stats(),
            'cpu_usage': self._cpu_usage,
            'gpu_usage': self._gpu_usage,
            'mem_usage': self._mem_usage,
            'layer_stats': self.get_layer_stats()
        }
        t1 = time.perf_counter()
        logger.debug(f"get_results finished. Duration: {t1 - t0}")
        return dict_

    def get_layer_stats(self):
        all_stats = {}

        for layer_id, tracker in self._input_trackers.items():
            all_stats[layer_id] = tracker.save()

        for layer_id, stats in self._inner_layers_stats_tracker.save().items():
            all_stats[layer_id] = stats

        for layer_id, tracker in self._output_trackers.items():
            all_stats[layer_id] = tracker.save()

        return all_stats

    def get_global_stats(self):
        """ Returns a stats object for the current global stats """
        return self._global_stats_tracker.save()

    def get_output_stats(self) -> Dict:
        """ Returns a stats object representing the current state of the outputs """
        output_stats = {
            layer_id: tracker.save()
            for layer_id, tracker in self._output_trackers.items()
        }
        return output_stats

    def get_output_stats_summaries(self):
        """ Collect summary dicts from all output layers and add them to a list """
        all_output_stats = self.get_output_stats()

        all_summaries = []
        for output_stats in all_output_stats.values():
            summary = output_stats.get_summary()
            all_summaries.append(summary)

        return all_summaries

    def _resolve_optimizer(self, training_settings):
        optimizer = training_settings['Optimizer']
        learning_rate = training_settings['Learning_rate']
        momentum = training_settings['Momentum']
        beta_1 = training_settings['Beta1']
        beta_2 = training_settings['Beta2']
        centered = training_settings['Centered']

        if isinstance(learning_rate, str):
            learning_rate = float(learning_rate)
        if isinstance(momentum, str):
            momentum = float(momentum)
        if isinstance(beta_1, str):
            beta_1 = float(beta_1)
        if isinstance(beta_2, str):
            beta_2 = float(beta_2)

        if optimizer == 'SGD':
            return tf.keras.optimizers.SGD(learning_rate=learning_rate, momentum=momentum)
        elif optimizer == 'ADAM':
            return tf.keras.optimizers.Adam(learning_rate=learning_rate, beta_1=beta_1, beta_2=beta_2)
        elif optimizer == 'Adagrad':
            return tf.keras.optimizers.Adagrad(learning_rate=learning_rate)
        elif optimizer == 'RMSprop':
            return tf.keras.optimizers.RMSprop(learning_rate=learning_rate, centered=centered)

    def _resolve_loss_function(self, training_settings):
        loss = training_settings['Loss']
        if loss == 'Quadratic':
            return tf.keras.losses.MeanSquaredError()
        elif loss == 'Cross-Entropy':
            return tf.keras.losses.CategoricalCrossentropy()
        elif loss == 'Dice':
            return dice
        else:
            raise NotImplementedError(f"No loss function called 'loss'")

    def _setup_loss_functions(self, training_settings):
        """ Creates a dict of losses, one per output """
        loss_function = self._resolve_loss_function(training_settings)

        losses = {
            layer_spec.feature_name: loss_function
            for layer_spec in self._graph_spec.layers
            if layer_spec.is_target_layer
        }
        return losses

    def _get_training_set(self):
        """ Gets a training set matching the training settings """
        return self._get_dataset('training', shuffle=self._shuffle_training_set)

    def _get_validation_set(self):
        """ Gets a validation set matching the training settings """
        return self._get_dataset('validation', shuffle=False)

    def _get_dataset(self, partition, shuffle):
        indexed_dataset = self._data_loader.get_dataset(
            partition=partition,
            shuffle=shuffle,
            drop_index=False  # Drop the index manually so we can inspect the rows used
        )

        if settings.TRAINING_DUMP_ROWS is not None:
            self._dump_dataset_rows(partition, indexed_dataset)

        dataset = self._data_loader \
                      .drop_dataset_index(indexed_dataset) \
                      .batch(self.batch_size)
        return dataset

    def _dump_dataset_rows(self, partition, indexed_dataset):
        indices = [row.numpy() for row, _, _, in indexed_dataset]

        df = self._data_loader.get_data_frame(partition='original')
        df = df.iloc[indices]

        path = f"data_epoch_{self._num_epochs_completed}_{partition}.csv"
        df.to_csv(path, index=True)
        logger.info(f"Saved data dump to {path}")

    @property
    def model_id(self):
        return self._model_id

    @property
    def session_id(self):
        return self.training_session_id

    @property
    def training_session_id(self):
        return self._training_session_id

