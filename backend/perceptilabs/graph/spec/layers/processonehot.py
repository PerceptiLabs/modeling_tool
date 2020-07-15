from typing import Tuple, Dict

from perceptilabs.graph.spec.layers import LayerSpec, LayerSpecBuilder, ParamSpec


class ProcessOneHotSpec(LayerSpec):
    _parameters = [
        ParamSpec('n_classes', (int,), None, 'The number of classes')
    ]


class ProcessOneHotBuilder(LayerSpecBuilder):
    target_class = ProcessOneHotSpec
        
    def from_dict(self, id_: str, dict_: Dict):
        self.from_dict_base(id_, dict_)
        if 'Properties' in dict_ and dict_['Properties'] is not None:                                
            self.set_parameter('n_classes', int(dict_['Properties']['N_class']))
        return self

    def to_dict(self, existing: LayerSpec) -> Dict:
        dict_ = self.to_dict_base(existing)
        dict_['Properties'] = {
            'N_class': existing.n_classes
        }
        return dict_
