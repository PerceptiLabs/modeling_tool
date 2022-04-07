from typing import Tuple, Dict, Any, Union
from pathlib import Path
import os

from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec


class LayerTfModelSpec(InnerLayerSpec):
    type_: str = "LayerTfModel"
    url: str = "https://tfhub.dev/sayakpaul/vit_s16_classification/1"
    trainable: bool = False

    @classmethod
    def _from_dict_internal(
        cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]
    ) -> LayerSpec:
        if "Properties" in dict_ and dict_["Properties"] is not None:
            params["url"] = dict_["Properties"]["url"]
            params["trainable"] = dict_["Properties"]["trainable"]

        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        """Deconstructs a layer spec into a 'json network' layer dict"""
        props = {}

        props["trainable"] = self.trainable
        props["url"] = self.url
        dict_["Properties"] = props

        return dict_
