from typing import Tuple, Dict, Any


from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec


class ProcessOneHotSpec(InnerLayerSpec):
    type_: str = 'ProcessOneHot'
    n_classes: int = 10
    
    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:                        
            params['n_classes'] = int(dict_['Properties']['N_class'])
            
        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:            
        """ Deconstructs a layer spec into a 'json network' layer dict """
        dict_['Properties'] = {
            'N_class': self.n_classes
        }
        return dict_
    
