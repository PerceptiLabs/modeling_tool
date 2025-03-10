from collections import namedtuple
from typing import Dict

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.graph.builder import GraphSpecBuilder

from perceptilabs.automation.modelrecommender.encoders import (
    NumericalEncoderBlueprint,
    ImageEncoderBlueprint,
    BinaryEncoderBlueprint,
    CategoricalEncoderBlueprint,
    TextEncoderBlueprint,
)
from perceptilabs.automation.modelrecommender.decoders import (
    NumericalDecoderBlueprint,
    CategoricalDecoderBlueprint,
    ImageDecoderBlueprint,
    MaskDecoderBlueprint,
)

from perceptilabs.automation.modelrecommender.siso_models import (
    SegmentationModel,
    ObjectDetectionModel,
)


class ModelRecommender:
    def __init__(self, data_loader=None):
        self._data_loader = data_loader

    def get_graph(self, feature_specs):
        """Takes a dictionary of feature specs and generates a graph spec for it
        Arguments:
            feature_specs: Mapping from feature name to feature spec
        Returns:
            a GraphSpec
        """
        builder = GraphSpecBuilder()

        num_inputs = len(
            [
                feature_spec
                for _, feature_spec in feature_specs.items()
                if feature_spec.iotype == "input"
            ]
        )
        num_outputs = len(
            [
                feature_spec
                for _, feature_spec in feature_specs.items()
                if feature_spec.iotype == "target"
            ]
        )
        target_datatypes = [
            feature_spec.datatype
            for _, feature_spec in feature_specs.items()
            if feature_spec.iotype == "target"
        ]

        if (
            num_inputs == 1
            and num_outputs == 1
            and target_datatypes in [["mask"], ["boundingbox"]]
        ):
            return self.get_single_input_single_output_network(feature_specs, builder)
        else:
            return self.get_encoder_decoder_network(feature_specs, builder)

    def get_single_input_single_output_network(self, feature_specs, builder):
        for feature_name, feature_spec in feature_specs.items():
            if feature_spec.iotype == "input":
                input_datatype = feature_spec.datatype
                input_feature_name = feature_name
                input_feature_spec = feature_spec
            if feature_spec.iotype == "target":
                target_datatype = feature_spec.datatype
                target_feature_name = feature_name
                target_feature_spec = feature_spec
        if input_datatype == "image" and target_datatype == "mask":
            SegmentationModel().build(
                builder,
                input_feature_name,
                target_feature_name,
                input_feature_spec,
                target_feature_spec,
                data_loader=self._data_loader,
            )
        if input_datatype == "image" and target_datatype == "boundingbox":
            ObjectDetectionModel().build(
                builder,
                input_feature_name,
                target_feature_name,
                input_feature_spec,
                target_feature_spec,
                data_loader=self._data_loader,
            )
        graph_spec = builder.build()
        return graph_spec

    def get_encoder_decoder_network(self, feature_specs, builder):
        encoder_end_nodes = []
        decoder_start_nodes = []

        for feature_name, feature_spec in feature_specs.items():
            if feature_spec.iotype == "input":
                end_node = self._add_encoder(builder, feature_name, feature_spec)
                encoder_end_nodes.append(end_node)
            elif feature_spec.iotype == "target":
                start_node = self._add_decoder(builder, feature_name, feature_spec)
                decoder_start_nodes.append(start_node)
            else:
                raise ValueError(
                    f"Feature {feature_name} must have iotype 'input' or 'target'"
                )

        self._connect_encoders_and_decoders(
            builder, encoder_end_nodes, decoder_start_nodes
        )

        graph_spec = builder.build()
        return graph_spec

    def _connect_encoders_and_decoders(
        self, builder, encoder_end_nodes, decoder_start_nodes
    ):
        """Merges the encoders and feeds the merged target to the decoders. If single input/target, no merge layer is needed."""
        num_encoders = len(encoder_end_nodes)

        if num_encoders == 1:
            combiner_id = encoder_end_nodes[0]
        else:
            combiner_id = builder.add_layer(
                "MathMerge",
                settings={
                    "input_count": num_encoders,
                    "merge_type": "Concat",
                    "merge_dim": 1,
                },
            )

            for i, layer_id in enumerate(encoder_end_nodes):
                builder.add_connection(layer_id, "output", combiner_id, f"input{i+1}")

        for layer_id in decoder_start_nodes:
            builder.add_connection(combiner_id, "output", layer_id, "input")

    def _add_encoder(self, builder, feature_name, feature_spec):
        """Encoder for a feature"""
        if feature_spec.datatype == "numerical":
            return NumericalEncoderBlueprint().build(
                builder, feature_name, feature_spec, data_loader=self._data_loader
            )
        if feature_spec.datatype == "text":
            return TextEncoderBlueprint().build(
                builder, feature_name, feature_spec, data_loader=self._data_loader
            )
        elif feature_spec.datatype == "image":
            return ImageEncoderBlueprint().build(
                builder, feature_name, feature_spec, data_loader=self._data_loader
            )
        elif feature_spec.datatype == "binary":
            return self._add_binary_encoder(builder, feature_name, feature_spec)
        elif feature_spec.datatype == "categorical":
            return self._add_categorical_encoder(
                builder, feature_name, feature_spec, data_loader=self._data_loader
            )
        else:
            raise NotImplementedError(
                f"No encoder found for datatype '{feature_spec.datatype}'"
            )

    def _add_decoder(self, builder, feature_name, feature_spec):
        """Decoder for a feature"""
        if feature_spec.datatype == "numerical":
            return NumericalDecoderBlueprint().build(
                builder, feature_name, feature_spec, data_loader=self._data_loader
            )
        elif feature_spec.datatype == "categorical":
            return CategoricalDecoderBlueprint().build(
                builder, feature_name, feature_spec, data_loader=self._data_loader
            )
        elif feature_spec.datatype == "binary":
            return CategoricalDecoderBlueprint().build(
                builder, feature_name, feature_spec, data_loader=self._data_loader
            )
        elif feature_spec.datatype == "image":
            return ImageDecoderBlueprint().build(
                builder, feature_name, feature_spec, data_loader=self._data_loader
            )
        elif feature_spec.datatype == "mask":
            return MaskDecoderBlueprint().build(
                builder, feature_name, feature_spec, data_loader=self._data_loader
            )
        else:
            raise NotImplementedError(
                f"No decoder found for datatype '{feature_spec.datatype}'"
            )

    def _add_numerical_encoder(self, builder, feature_name, feature_spec):
        """Adds a numerical encoder"""
        return NumericalEncoderBlueprint().build(builder, feature_name, feature_spec)

    def _add_image_encoder(self, builder, feature_name, feature_spec):
        """Adds a image encoder"""
        return ImageEncoderBlueprint().build(builder, feature_name, feature_spec)

    def _add_binary_encoder(self, builder, feature_name, feature_spec):
        """Adds a binary encoder"""
        return BinaryEncoderBlueprint().build(builder, feature_name, feature_spec)

    def _add_categorical_encoder(
        self, builder, feature_name, feature_spec, data_loader
    ):
        return CategoricalEncoderBlueprint().build(
            builder, feature_name, feature_spec, data_loader
        )

    def _add_numerical_decoder(self, builder, feature_name, feature_spec):
        """Adds a numerical decoder"""
        return NumericalDecoderBlueprint().build(builder, feature_name, feature_spec)
