from typing import Tuple, Dict, Any, Union
from pathlib import Path
import os

from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec


class LayerObjectDetectionModelSpec(InnerLayerSpec):
    type_: str = "LayerObjectDetectionModel"
    url: str = "https://tfhub.dev/tensorflow/efficientdet/lite0/feature-vector/1"
    trainable: bool = False
    aspect_ratios: list = [1.0, 2.0, 0.5]
    anchor_scale: float = 4.0
    num_scales: int = 3
    min_level = 3
    max_level = 7
    data_format: str = "channels_last"
    positives_momentum = 0.3
    box_class_repeats = 3
    fpn_cell_repeats = 3
    fpn_num_filters = 88
    separable_conv = True
    apply_bn_for_resampling = True
    conv_after_downsample = False
    conv_bn_act_pattern = False
    drop_remainder = True
    num_classes = 1

    @classmethod
    def _from_dict_internal(
        cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]
    ) -> LayerSpec:
        if "Properties" in dict_ and dict_["Properties"] is not None:
            params["url"] = dict_["Properties"]["url"]
            params["trainable"] = dict_["Properties"]["trainable"]
            params["aspect_ratios"] = dict_["Properties"]["aspect_ratios"]
            params["anchor_scale"] = dict_["Properties"]["anchor_scale"]
            params["num_scales"] = dict_["Properties"]["num_scales"]
            params["num_classes"] = dict_["Properties"]["num_classes"]

        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        """Deconstructs a layer spec into a 'json network' layer dict"""
        props = {}

        props["trainable"] = self.trainable
        props["url"] = self.url
        props["num_scales"] = self.num_scales
        props["aspect_ratios"] = self.aspect_ratios
        props["anchor_scale"] = self.anchor_scale
        props["num_classes"] = self.num_classes
        dict_["Properties"] = props

        return dict_
