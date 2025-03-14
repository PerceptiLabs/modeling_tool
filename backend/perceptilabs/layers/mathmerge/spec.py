from typing import Tuple, Dict, Any, Union

from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec
from perceptilabs.layers.utils import try_cast


class MathMergeSpec(InnerLayerSpec):
    type_: str = "MathMerge"
    merge_type: Union[str, None] = None
    merge_dim: Union[int, None] = None
    input_count: int = 2

    @classmethod
    def _from_dict_internal(
        cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]
    ) -> LayerSpec:
        if "Properties" in dict_:
            params["input_count"] = dict_["Properties"]["InputsCount"]
            params["merge_type"] = dict_["Properties"]["Type"]
            params["merge_dim"] = try_cast(dict_["Properties"]["Merge_dim"], int)

        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        dict_["Properties"] = {}
        dict_["Properties"]["Type"] = self.merge_type
        dict_["Properties"]["Merge_dim"] = str(self.merge_dim)
        dict_["Properties"]["Merge_order"] = None
        dict_["Properties"]["InputsCount"] = self.input_count
        return dict_
