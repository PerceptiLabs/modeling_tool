from typing import Tuple, Dict, Any, Union

from perceptilabs.layers.specbase import LayerSpec, LayerConnection, InnerLayerSpec


class MathSwitchSpec(InnerLayerSpec):
    type_: str = 'MathSwitch'
    selected_layer_id: Union[str, None] = "input1" 
    selected_var_name: Union[str, None] = "input1"
    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:

        conn_specs = dict_['backward_connections']
        for conn_spec in conn_specs:
            if conn_spec['dst_var'] == 'input1':
                params['selected_var_name'] = 'input1'

                params['selected_layer_id'] = conn_spec['src_id']
                break
            else:
                params['selected_var_name'] = 'input2'
                params['selected_layer_id'] = conn_spec['src_id']           

        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        props={
            'selected_layer_id':self.selected_layer_id,
            'selected_var_name':self.selected_var_name
        }
        dict_['Properties'] = props
        return dict_
