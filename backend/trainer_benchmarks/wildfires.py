import time
import tensorflow as tf
import os
import pkg_resources

from perceptilabs.script import ScriptFactory
from trainer_benchmarks.suite import BenchmarkSuite
import perceptilabs.data.utils as data_utils
from perceptilabs.trainer.base import Trainer, TrainingModel
from perceptilabs.graph.builder import GraphSpecBuilder


class WildfiresSuite(BenchmarkSuite):
    def __init__(self):
        self.data_loader = data_utils.get_wildfire_loader()

    def _get_trainer_results(self, trainer, training_settings, training_duration):
        """ Formats the results summary of a PerceptiLabs recommended model. The output dict should match the baseline 

        Arguments:
            trainer: the trainer used 
            training_settings: the settings used
            training_duration: the training duration in seconds

        Returns:
            a dictionary of metrics and their values
        """
        stats = next(iter(trainer.get_output_stats().values())
                     )  # This dataset has a single output
        results = stats.get_summary()
        results['training_duration (s)'] = training_duration
        results['epoch_duration (ms)'] = training_duration / \
            int(training_settings['Epochs']) * 1000
        results['num_epochs'] = int(training_settings['Epochs'])
        return results

    def _run_custom_model(self):
        path = os.path.join(data_utils.get_tutorial_data_directory(),
                            'Wildfires', 'data.csv')
        builder = GraphSpecBuilder()

        c1 = builder.add_layer('IoInput',
                               settings={'datatype': 'image', 'feature_name': 'images', 'file_path': path})
        c2 = builder.add_layer('DeepLearningConv', settings={'conv_type': 'Conv',
                                                             'conv_dim': '2D',
                                                             'patch_size': 3,
                                                             'feature_maps': 64,
                                                             'stride': 1,
                                                             'activation': 'ReLU',
                                                             'batch_norm': True,
                                                             'dropout': False,
                                                             'keep_prob': 0.5,
                                                             'padding': 'VALID',
                                                             'pool': True,
                                                             'pooling': 'Max',
                                                             'pool_padding': 'VALID',
                                                             'pool_area': 2,
                                                             'pool_stride': 2})
        c3 = builder.add_layer('DeepLearningConv', settings={'conv_type': 'Conv',
                                                             'conv_dim': '2D',
                                                             'patch_size': 3,
                                                             'feature_maps': 64,
                                                             'stride': 1,
                                                             'activation': 'ReLU',
                                                             'padding': 'VALID',
                                                             'pool': True,
                                                             'pooling': 'Max',
                                                             'pool_padding': 'VALID',
                                                             'pool_area': 2,
                                                             'pool_stride': 2})
        c4 = builder.add_layer('DeepLearningConv', settings={'conv_type': 'Conv',
                                                             'conv_dim': '2D',
                                                             'patch_size': 3,
                                                             'feature_maps': 64,
                                                             'stride': 1,
                                                             'activation': 'ReLU',
                                                             'padding': 'VALID',
                                                             'pool': True,
                                                             'pooling': 'Max',
                                                             'pool_padding': 'VALID',
                                                             'pool_area': 2,
                                                             'pool_stride': 2})
        c5 = builder.add_layer('DeepLearningFC',
                               settings={'n_neurons': 128, 'activation': 'ReLU', 'batch_norm': True, 'dropout': False, 'keep_prob': 0.5})
        c6 = builder.add_layer('DeepLearningFC',
                               settings={'n_neurons': 2, 'activation': 'Softmax'})
        c7 = builder.add_layer('IoOutput',
                               settings={'datatype': 'categorical', 'feature_name': 'labels', 'file_path': path})
        builder.add_connection(
            source_id=c1, source_var='output', dest_id=c2, dest_var='input')
        builder.add_connection(c2, 'output', c3, 'input')
        builder.add_connection(c3, 'output', c4, 'input')
        builder.add_connection(c4, 'output', c5, 'input')
        builder.add_connection(c5, 'output', c6, 'input')
        builder.add_connection(c6, 'output', c7, 'input')
        graph_spec = builder.build()

        training_settings = {'Epochs': '8',
                             'Batch_size': '32',
                             'Shuffle': True,
                             'Loss': 'Quadratic',
                             'Learning_rate': 0.001,
                             'Optimizer': 'ADAM',
                             'Beta1': 0.9,
                             'Beta2': 0.999,
                             'Momentum': 0,
                             'Centered': False,
                             'AutoCheckpoint': False}
        script_factory = ScriptFactory()
        training_model = TrainingModel(script_factory, graph_spec)
        trainer = Trainer(self.data_loader, training_model, training_settings)
        t0 = time.perf_counter()
        trainer.run()
        dt = time.perf_counter() - t0

        results = self._get_trainer_results(trainer, training_settings, dt)
        return results

    def _get_trainer_results(self, trainer, training_settings, training_duration):
        """ Formats the results summary of a PerceptiLabs recommended model or custom model. The output dict should match the baseline

        Arguments:
            trainer: the trainer used 
            training_settings: the settings used
            training_duration: the training duration in seconds

        Returns:
            a dictionary of metrics and their values
        """
        stats = next(iter(trainer.get_output_stats().values())
                     )  # This dataset has a single output
        results = stats.get_summary()
        results['training_duration (s)'] = training_duration
        results['epoch_duration (ms)'] = training_duration / \
            int(training_settings['Epochs']) * 1000
        results['num_epochs'] = int(training_settings['Epochs'])
        return results
