import os
import logging
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Type, Any, List, Union
from collections import namedtuple

from pydantic import BaseModel, validator

from perceptilabs.utils import stringify, MyPydanticBaseModel
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.layers.specutils as specutils
from perceptilabs.graph import AbstractGraphSpec

logger = logging.getLogger(APPLICATION_LOGGER)


def sanitize_name(name):
    name = name.replace(' ', '_')
    name = '_' + name
    return name


class LayerConnection(MyPydanticBaseModel):
    src_id: str = None
    src_var: str = None
    dst_id: str = None
    dst_var: str = None

    class Config:
        allow_mutation = False

    @validator('src_id', 'src_var', 'dst_id', 'dst_var')
    def _check_not_none(cls, value):
        if value is None:
            raise ValueError('cannot be None')
        return value

    def __hash__(self):
        return hash(self.src_id + self.src_var + self.dst_id + self.dst_var)

    def get_src_sanitized_name(self, graph_spec: AbstractGraphSpec) -> str:
        """ Looks up the 'sanitized name' of the source layer """
        return self._get_sanitized_name(self.src_id, graph_spec)        

    def get_dst_sanitized_name(self, graph_spec: AbstractGraphSpec) -> str:
        """ Looks up the 'sanitized name' of the destination layer """        
        return self._get_sanitized_name(self.dst_id, graph_spec)

    def _get_sanitized_name(self, layer_id, graph_spec):
        layer = graph_spec.nodes_by_id.get(layer_id)
        return layer.sanitized_name if layer is not None else None
    
    
class LayerSpec(ABC, MyPydanticBaseModel):
    id_: str = None
    name: str = None
    type_: str = None
    preview_variable: str = ''
    get_preview: bool = False
    backward_connections: Tuple[LayerConnection, ...] = ()
    forward_connections: Tuple[LayerConnection, ...] = ()
    visited: bool = False
    custom_code: Union[str, None] = None
    end_points: Union[Tuple[str, ...], None] = ()

    class Config:
        allow_mutation = False

    def has_input_variable(self, var_name):
        return var_name in (conn.dst_var for conn in self.backward_connections)
        
    def clone(self, modified_params: Dict[str, Any]=None) -> 'LayerSpec':
        """ Creates a modified version of the layer spec """
        
        modified_params = modified_params or {}
        params = {}

        for field_name in self.field_names:
            params[field_name] = getattr(self, field_name)

        params.update(modified_params)
        return self.__class__(**params)

    @property
    def field_names(self):
        """ The fields of this layer spec. """
        if hasattr(self, 'fields'):  # Pydantic >= 1.8.0 does not have the fields property.
            return list(self.fields.keys())
        else:
            return list(dict(self))           

    def compute_field_hash(self, ignore_forward_connections=True, prefer_custom_code=True):
        """ Computes a hash based on a _subset_ of the fields.

        Computes a hash based on the fields. This method is kept distinct from a __hash__ implementation since we have the option to ignore forward connections and ids.

        args:
            ignore_forward_connections: if true, skip forward connections.
            prefer_custom_code: if true, the hash will be based on that only. 
        """
        ignored_fields = ['id_', 'name', 'visited', 'preview_variable', 'get_preview']

        if prefer_custom_code and self.custom_code is not None:
            return hash(self.custom_code)
        else:
            field_hashes = 0
            for field_name in self.field_names:
                if field_name in ignored_fields:
                    continue
                if ignore_forward_connections and field_name == 'forward_connections':
                    continue

                field_value = getattr(self, field_name)
                try:
                    field_hashes += hash(field_name+str(hash(field_value)))
                except TypeError:
                    logger.exception(f"Failed hashing field {field_name} with type {type(field_value)} in layer {self.id_} [{self.type_}]")
                    raise     
            return hash(field_hashes)
        
    @classmethod
    def from_dict(cls, id_: str, dict_: Dict[str, Any]):
        """ Loads a 'json network' layer dict into a LayerSpec. 

        This method contains parameters that are common to each spec. Specifics are loaded using _from_dict_internal
        """


        def repl_smp(x):
            # TEMPORARY FIX
            if x == '(sample)':
                x = 'output'
            return x
        
        def resolve_bw_cons(dict_):
            return tuple(
                LayerConnection(src_id=conn_spec['src_id'], src_var=repl_smp(conn_spec['src_var']), dst_id=id_, dst_var=conn_spec['dst_var'])
                for conn_spec in dict_['backward_connections']
            )

        def resolve_fw_cons(dict_):
            return tuple(
                LayerConnection(src_id=id_, src_var=repl_smp(conn_spec['src_var']), dst_id=conn_spec['dst_id'], dst_var=conn_spec['dst_var'])                
                for conn_spec in dict_['forward_connections']
            )
            
        def resolve_custom_code(dict_):
            if dict_['Code'] is not None and 'Output' in dict_['Code']:
                custom_code = dict_['Code']['Output']
            else:
                custom_code = dict_['Code']
            
            if custom_code is not None and custom_code.strip() == '':
                custom_code = None
            return custom_code
        
        params = {
            'id_': str(id_),
            'name': dict_.get('Name'),
            'type_': dict_.get('Type'),
            'visited': dict_.get('visited', False),
            'preview_variable': dict_.get('previewVariable', ''),
            'get_preview': dict_.get('getPreview', False),                        
            'end_points': tuple(dict_.get('endPoints', ())),
            'backward_connections': resolve_bw_cons(dict_),
            'forward_connections': resolve_fw_cons(dict_),
            'custom_code': resolve_custom_code(dict_)
        }
        return cls._from_dict_internal(id_, dict_, params)


    def to_dict(self) -> Dict[str, Any]:
        """ Deconstructs the spec into a 'json network' layer dict 

        This method contains parameters that are common to each spec. Specifics are deconstructed using _to_dict_internal
        """
        
        dict_ = {}
        dict_['Name'] = self.name
        dict_['Type'] = self.type_
        dict_['Code'] = self.custom_code
        dict_['visited'] = self.visited
        dict_['previewVariable'] = self.preview_variable
        dict_['getPreview'] = self.get_preview        
        dict_['endPoints'] = list(self.end_points)

        dict_['backward_connections'] = [
            {
                'src_id': c.src_id,
                'src_var': c.src_var,
                'dst_var': c.dst_var
            }            
            for c in self.backward_connections
        ]
        dict_['forward_connections'] = [
            {
                'dst_id': c.dst_id,
                'dst_var': c.dst_var,
                'src_var': c.src_var
            }            
            for c in self.forward_connections
        ]
        
        return self._to_dict_internal(dict_)

    @abstractmethod
    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        """ Deconstructs a layer spec into a 'json network' layer dict """
        raise NotImplementedError        
            
    @property
    def sanitized_name(self) -> str:
        """ Name with spaces replaced by underscore, as well as a prepended underscore. Prepended layer type """
        if self.type_ and self.name:
            return self.type_ + sanitize_name(self.name)
        else:
            return None

    def __str__(self):
        return f"{self.__class__.__name__} (name: {self.name}, id: {self.id_}, type: {self.type_})"

    def __repr__(self):
        return str(self) + '\n' + stringify(self.to_dict())
    
    @property
    def should_show_errors(self):
        """ Returns true if the user has configured the component.

        Some classes can be partially configured. For example, DataData layers whose file paths aren't specified."""
        return self.visited

    @property
    def is_training_layer(self):
        return False

    @property
    def is_data_layer(self):
        return False

    @property
    def is_inner_layer(self):
        return False

    @property
    def is_target_layer(self):
        return False
    
    @property
    def is_input_layer(self):
        return False

    def is_ancestor_to(self, layer_spec, graph_spec):
        return (layer_spec == self) or (self in graph_spec.get_ancestors(layer_spec))

    @property
    def is_fully_configured(self):
        """ If some configuration is missing. E.g., labels connection for a training layer """
        return True

    @property
    def input_connections(self):
        """ Alias for backward connections """
        return self.backward_connections
    
    @property
    def output_connections(self):
        """ Alias for forward connections """
        return self.forward_connections        

    
class IoLayerSpec(LayerSpec):
    @property
    def should_show_errors(self):
        """ Always show errors for IoLayers """
        return True
    

class InnerLayerSpec(LayerSpec):
    @property
    def should_show_errors(self):
        """ Show errors if visited or if there are outgoing or ingoing connections """
        return super().should_show_errors or len(self.forward_connections) > 0 or len(self.backward_connections) > 0
    
    @property
    def is_inner_layer(self):
        return True


class TrainingLayerSpec(InnerLayerSpec):
    @property
    def is_training_layer(self):
        return True
    
    @property
    def is_inner_layer(self):
        return False

    
class DataLayerSpec(InnerLayerSpec):
    @property
    def is_data_layer(self):
        return True

    @property
    def is_inner_layer(self):
        return False

    
class DummySpec(LayerSpec):
    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        pass

    
