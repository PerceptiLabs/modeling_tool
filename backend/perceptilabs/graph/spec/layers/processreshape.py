from typing import Tuple, Dict

from perceptilabs.graph.spec.layers import LayerSpec, LayerSpecBuilder, ParamSpec


class ProcessReshapeSpec(LayerSpec):
    _parameters = [
        ParamSpec('shape', (tuple,), (1, 1, 1), 'The target shape'),
        ParamSpec('permutation', (tuple,), (0, 1, 2), 'The order by which the dimensions are permuted')        ]


class ProcessReshapeBuilder(LayerSpecBuilder):
    target_class = ProcessReshapeSpec

    def from_dict(self, id_: str, dict_: Dict):
        self.from_dict_base(id_, dict_)

        if 'Properties' in dict_ and dict_['Properties'] is not None:                                
            self.set_parameter('shape', tuple(dict_['Properties']['Shape']))
            self.set_parameter('permutation', tuple(dict_['Properties']['Permutation']))
        return self

    def to_dict(self, existing: LayerSpec) -> Dict:
        dict_ = self.to_dict_base(existing)        
        dict_['Properties'] = {
            'Shape': existing.shape,
            'Permutation': existing.permutation
        }
        return dict_
        
