import os
import psutil
from typing import Dict
import numpy as np

from perceptilabs.autosettings import InferenceRule
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.graph.spec.layers import LayerSpec, LayerSpecBuilder, get_layer_builder
from perceptilabs.core_new.lightweight2 import LayerResults


class DeepLearningFcOutputShapeFromLabels(InferenceRule):
    def is_topologically_valid(self, graph_spec, layer_spec):
        if layer_spec.type != 'DeepLearningFC':
            return False, []

        successors = graph_spec.get_successors(layer_spec)
        if len(successors) != 1:
            return False, []

        if successors[0].type != 'TrainNormal':
            return False, []

        if successors[0].layer_true is None:
            return False, []

        self._labels_id = successors[0].layer_true
        layer_spec_true = graph_spec.nodes_by_id[self._labels_id]
        return True, [layer_spec_true]

    def is_applicable(self, graph_spec: GraphSpec, layer_spec: LayerSpec, lw_results: Dict[str, LayerResults]) -> bool:
        if not hasattr(self, '_labels_id'):
            return False

        self._labels_shape = lw_results[self._labels_id].out_shape
        if len(self._labels_shape) > 1:
            return False
        return True

    def apply(self, graph_spec: GraphSpec, layer_spec: LayerSpec, builder: LayerSpecBuilder, lw_results: Dict[str, LayerResults]) -> None:
        """ A new layer will be created based on the builder configuration """

        if len(self._labels_shape) == 0:
            n_classes = 1
        elif len(self._labels_shape) == 1:
            n_classes = self._labels_shape[0]
        else:
            raise RuntimeError        
        
        builder.set_parameter('n_neurons', n_classes)


class DeepLearningConvDoubleFeatureMaps(InferenceRule):
    # Double the number of feature maps if the successor is also a conv layer..

    def is_topologically_valid(self, graph_spec: GraphSpec, layer_spec: LayerSpec):    
        if layer_spec.type != 'DeepLearningConv':
            return False, []
        
        predecessors = graph_spec.get_predecessors(layer_spec)
        if len(predecessors) != 1:
            return False, []

        if predecessors[0].type != 'DeepLearningConv':
            return False, []
        
        self._prev_conv_id = predecessors[0].id        
        return True, [predecessors[0]]

    def is_applicable(self, graph_spec: GraphSpec, layer_spec: LayerSpec, lw_results: Dict[str, LayerResults]) -> bool:
        return hasattr(self, '_prev_conv_id')
    
    def apply(self, graph_spec: GraphSpec, layer_spec: LayerSpec, builder: LayerSpecBuilder, lw_results: Dict[str, LayerResults]) -> None:
        """ A new layer will be created based on the builder configuration """

        prev_conv = graph_spec.nodes_by_id[self._prev_conv_id]
        print('prev feature maps', prev_conv.feature_maps)

        
        #import pdb; pdb.set_trace()
        builder.set_parameter('feature_maps', 2*prev_conv.feature_maps)

        
class DataDataShouldUseLazy(InferenceRule):
    MAX_RAM_USAGE = 0.3 # Fraction of total memory that can be used for the datasets. If exceeded, toggle lazy

    def is_topologically_valid(self, graph_spec: GraphSpec, layer_spec: LayerSpec):
        return layer_spec.type == 'DataData', []
        
    def is_applicable(self, graph_spec: GraphSpec, layer_spec: LayerSpec, lw_results: Dict[str, LayerResults]) -> bool:
        if layer_spec.type != 'DataData':
            return False

        if any(s.type != 'file' for s in layer_spec.sources):
            return False        

        est_ram_size = sum(self._estimate_ram_size(s.path) for s in layer_spec.sources)
        tot_ram = psutil.virtual_memory().total

        if est_ram_size < tot_ram * self.MAX_RAM_USAGE:
            return False
        return True

    def _estimate_ram_size(self, path):
        estimator = lambda path: 2*os.path.getsize(path) # Default to arbitrary safety margin        
        if path.endswith('csv'):
            import perceptilabs.insights.csv_ram_estimator as csv_ram_estimator
            estimator = csv_ram_estimator.get_instance()

        return estimator(path)

    def apply(self, graph_spec: GraphSpec, layer_spec: LayerSpec, builder: LayerSpecBuilder, lw_results: Dict[str, LayerResults]) -> None:
        """ A new layer will be created based on the builder configuration """        
        builder.set_parameter('lazy', True)
        
        
class ProcessReshape1DFromPrimeFactors(InferenceRule):
    MAX_DIM = 3 # To improve speed, we will not suggest factorizations with more than 3 dimensions
    MAX_LENGTH = 5000 # For large vectors the current implementation is slow.

    def is_topologically_valid(self, graph_spec: GraphSpec, layer_spec: LayerSpec):    
        if layer_spec.type != 'ProcessReshape':
            return False, []

        predecessors = graph_spec.get_predecessors(layer_spec)
        if len(predecessors) != 1:
            return False, []

        input_layer = predecessors[0]
        self._input_layer_id = input_layer.id
        return True, [input_layer]
        
    def is_applicable(self, graph_spec: GraphSpec, layer_spec: LayerSpec, lw_results: Dict[str, LayerResults]) -> bool:
        """ Checks whether the rule applies to the current layer and graph """
        if not hasattr(self, '_input_layer_id'):
            return False

        input_shape = lw_results[self._input_layer_id].out_shape
        if len(input_shape) != 1:
            return False

        input_length = input_shape[0]
        if input_length > self.MAX_LENGTH:
            return False

        self._factorizations = self._get_factorizations(input_length, max_factors=self.MAX_DIM) # Save this for later
        if len(self._factorizations) == 0:
            return False
        
        return True

    def apply(self, graph_spec: GraphSpec, layer_spec: LayerSpec, builder: LayerSpecBuilder, lw_results: Dict[str, LayerResults]) -> None:
        """ A new layer will be created based on the builder configuration """
        factorizations = [f if len(f) == 3 else f + [1] for f in self._factorizations] # Make them 3D

        scored_shapes = sorted(
            [(f, self._compute_shape_score(f)) for f in factorizations],
            key=lambda x: x[1],
            reverse=True
        )
        new_shape = tuple(scored_shapes[0][0]) # Select the one with the highest score
        builder.set_parameter('shape', new_shape)    

    def _compute_shape_score(self, shape):
        """ A set of simple rules to determine which of the shapes are best """
        score = 0
        
        # Favor square shapes
        diff = np.absolute(shape[0] - shape[1])
        score += 1.0 - (diff / (shape[0] + shape[1]))

        # Favor shapes where the third dimension is lower (common for images)        
        if shape[0] > shape[2] and shape[1] > shape[2]:
            score += 1

        # Favor shapes where the third dimension is 1 (for simplicity)            
        if shape[2] == 1:
            score += 1.5

            # Favor shapes where the third dimension is 3 or 1 (common for images)            
        if shape[2] == 3:
            score += 1.6
            
        return score
        
    def _get_factorizations(self, number, max_factors=None):
        # TODO: This is a very naive implementation and it will be slow for some cases. It is very likely this needs to be optimized in the future.

        def get_factorizations_recursive(number, current_factors, factorizations, max_factors):
            if max_factors and len(current_factors) > max_factors:
                return
            
            current_product = np.prod(current_factors)
            if current_product > number:
                return
            
            if current_product == number:
                factorizations.append(current_factors)
                return

            for factor in range(1, number):
                if factor*current_product > number:
                    break

                if number % factor == 0:
                    get_factorizations_recursive(number, current_factors + [factor], factorizations, max_factors)

        factorizations = []
        get_factorizations_recursive(number, [], factorizations, max_factors)
        return factorizations
        
        
if __name__ == "__main__":

    n_classes = 10    
    inputs_path = "/home/anton/Data/mnist_split/mnist_input.npy"
    labels_path = "/home/anton/Data/mnist_split/mnist_labels.npy"

    json_network = {
        "Layers": {
            "1": {
                "Name": "data_inputs",
                "Type": "DataData",
                "Properties": {
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": inputs_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Batch_size": 8,
                        "Shuffle_data": False,
                        "Columns": []                        
                    },
                },
                "backward_connections": [],
                "forward_connections": [["3", "reshape"]],
                "Code": None,
                "checkpoint": [],
                "endPoints": []               
            },
            "2": {
                "Name": "data_labels",
                "Type": "DataData",
                "Properties": {
                    "Type": "DataData",
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": labels_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Batch_size": 8,
                        "Shuffle_data": False,
                        "Columns": []
                    },
                },
                "backward_connections": [],
                "forward_connections": [["5", "one_hot"]],
                "Code": None,
                "checkpoint": [],
                "endPoints": [],                
            },
            "3": {
                "Name": "reshape",
                "Type": "ProcessReshape",                
                "Properties": {
                    "Shape": [12, 1, 3],
                    "Permutation": [0, 1, 2]
                },
                "backward_connections": [["1", "data_inputs"]],
                "forward_connections": [["3.1", "conv1"]],
                "Code": None,
                "checkpoint": [],
                "endPoints": [],                
            },
            "3.1": {
                "Name": "conv1",
                "Type": "DeepLearningConv",
                "checkpoint": [],
                "endPoints": [],
                "Properties": {
                    "Conv_dim": "2D",
                    "Patch_size": "3",
                    "Stride": "2",
                    "Padding": "SAME",
                    "Feature_maps": "8",
                    "Activation_function": "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1",
                    "PoolBool": False,
                    "Pooling": "Max",
                    "Pool_area": "2",
                    "Pool_padding": "SAME",
                    "Pool_stride": "2"
                },
                "Code": None,
                "backward_connections": [
                    ["3", "reshape"]
                ],
                "forward_connections": [
                    ["3.2", "conv2"]
                ]
            },

            "3.2": {
                "Name": "conv2",
                "Type": "DeepLearningConv",
                "checkpoint": [],
                "endPoints": [],
                "Properties": {
                    "Conv_dim": "2D",
                    "Patch_size": "3",
                    "Stride": "2",
                    "Padding": "SAME",
                    "Feature_maps": "8000",
                    "Activation_function": "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1",
                    "PoolBool": False,
                    "Pooling": "Max",
                    "Pool_area": "2",
                    "Pool_padding": "SAME",
                    "Pool_stride": "2"
                },
                "Code": None,
                "backward_connections": [
                    ["3.1", "conv1"]
                ],
                "forward_connections": [
                    ["4", "fc"]
                ]
            },            
            "4": {
                "Name": "fc",
                "Type": "DeepLearningFC",                
                "Properties": {
                    "Neurons": 123,
                    "Activation_function" : "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1"
                },
                "backward_connections": [["3.2", "conv2"]],
                "forward_connections": [["6", "training"]],
                "Code": None,
                "checkpoint": [],
                "endPoints": [],                
            },
            "5": {
                "Name": "one_hot",
                "Type": "ProcessOneHot",
                "Properties": {
                    "N_class": n_classes
                },
                "backward_connections": [["2", "data_labels"]],
                "forward_connections": [["6", "training"]],
                "Code": None,
                "checkpoint": [],
                "endPoints": [],                                
            },
            "6": {
                "Name": "training",
                "Type": "TrainNormal",
                "Properties": {
                    "Labels": "5",
                    "Loss": "Quadratic",
                    "Epochs": 200,
                    "Class_weights": "1",  # TODO: what's this?
                    "Optimizer": "SGD",
                    "Batch_size": 10,                                        
                    "Beta_1": "0.9",
                    "Beta_2": "0.999",
                    "Momentum": "0.9",
                    "Decay_steps": "100000",
                    "Decay_rate": "0.96",
                    "Learning_rate": "0.05",
                    "Distributed": False
                },
                "backward_connections": [["4", "fc"], ["5", "one_hot"]],
                "forward_connections": [],
                "Code": None,
                "checkpoint": [],
                "endPoints": [],                                
            }
        }
    }
    
    from perceptilabs.graph.spec import GraphSpec
    from perceptilabs.autosettings import SettingsEngine

    graph_spec = GraphSpec.from_dict(json_network)    
    
    rules = [
        DeepLearningFcOutputShapeFromLabels,
        ProcessReshape1DFromPrimeFactors,
        DeepLearningConvDoubleFeatureMaps,
        DataDataShouldUseLazy
    ]
    
    from perceptilabs.core_new.lightweight2 import LightweightCore
    engine = SettingsEngine(rules, lw_core=LightweightCore())
    rec_net = engine.run(graph_spec, graph_spec_tmp=json_network)
    
    import pdb; pdb.set_trace()    

    
    
        
