from typing import Tuple, Dict, Any, Union, List

from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec
from perceptilabs.layers.mixins import MixinDeepLearning
from perceptilabs.layers.utils import try_cast


class DeepLearningConvSpec(InnerLayerSpec, MixinDeepLearning):
    type_: str = "DeepLearningConv"
    batch_norm: bool = False
    dropout: bool = False
    keep_prob: float = 0.0
    conv_type: str = "Conv"
    conv_dim: str = "2D"
    patch_size: Union[int, None] = 3
    feature_maps: Union[int, None] = 8
    stride: Union[int, None] = 2
    padding: str = "SAME"
    activation: Union[str, None] = "Sigmoid"
    pool: bool = False
    pooling: Union[str, None] = None
    pool_padding: Union[str, None] = None
    pool_area: Union[int, None] = None
    pool_stride: Union[int, None] = None

    @classmethod
    def _from_dict_internal(
        cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]
    ) -> LayerSpec:
        """Converts the frontend JSON into a Python class"""
        if "Properties" in dict_ and dict_["Properties"] is not None:
            params["dropout"] = dict_["Properties"]["Dropout"]
            params["keep_prob"] = try_cast(dict_["Properties"]["Keep_prob"], float)
            params["batch_norm"] = try_cast(dict_["Properties"].get("Batch_norm"), bool)
            params["conv_type"] = str(dict_["Properties"].get("Conv_type", "Conv"))
            params["conv_dim"] = str(dict_["Properties"]["Conv_dim"])
            params["patch_size"] = (
                int(dict_["Properties"]["Patch_size"])
                if dict_["Properties"]["Patch_size"]
                else None
            )
            params["feature_maps"] = (
                int(dict_["Properties"]["Feature_maps"])
                if dict_["Properties"]["Feature_maps"]
                else None
            )
            params["stride"] = (
                int(dict_["Properties"]["Stride"])
                if dict_["Properties"]["Stride"]
                else None
            )
            params["padding"] = dict_["Properties"]["Padding"]
            params["activation"] = dict_["Properties"]["Activation_function"]

            params["pool"] = dict_["Properties"]["PoolBool"]
            params["pooling"] = dict_["Properties"]["Pooling"]
            params["pool_padding"] = str(dict_["Properties"]["Pool_padding"])
            params["pool_area"] = try_cast(dict_["Properties"].get("Pool_area"), int)
            params["pool_stride"] = try_cast(
                dict_["Properties"].get("Pool_stride"), int
            )

        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        """Deconstructs a layer spec into a 'json network' layer dict"""
        props = {}

        props["Dropout"] = self.dropout
        props["Keep_prob"] = self.keep_prob
        props["Batch_norm"] = self.batch_norm
        props["Conv_type"] = self.conv_type
        props["Conv_dim"] = self.conv_dim
        props["Patch_size"] = self.patch_size
        props["Feature_maps"] = self.feature_maps
        props["Stride"] = self.stride
        props["Padding"] = self.padding
        props["Activation_function"] = self.activation

        props["PoolBool"] = self.pool
        props["Pooling"] = self.pooling
        props["Pool_area"] = self.pool_area
        props["Pool_padding"] = self.pool_padding
        props["Pool_stride"] = self.pool_stride

        dict_["Properties"] = props

        return dict_
