import os
import logging
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Type, Any, List, Union
from collections import namedtuple

from pydantic import BaseModel

from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.layers.specutils as specutils

logger = logging.getLogger(APPLICATION_LOGGER)


def sanitize_name(name):
    name = name.replace(' ', '_')
    name = '_' + name
    return name


# -------------------- CYTHON WORKAROUND --------------------
#
# Cython doesn't yet play well with annotations (required for Pydantic).
# See https://github.com/cython/cython/issues/3776
#
# There is also an issue with Pydantic and Cython. See below. 
#
# This workaround BREAKS type checking for the compiled version, so therefore
# this workaround should be removed as soon as these issues are fixed.


import pydantic.main

class MyModelMetaclass(pydantic.main.ModelMetaclass):
    # Cython has not caught up with Python 3.7. So we have to create __annotations__ manually
    # for Pydantic to work.
    
    def __new__(mcs, name, bases, namespace, **kwargs):
        if '__annotations__' not in namespace:
            untouched_types = pydantic.main.UNTOUCHED_TYPES
            
            annotations = {}
            for var_name, value in namespace.items():
                if (
                        pydantic.main.is_valid_field(var_name)
                        and not isinstance(value, untouched_types)
                ):
                    annotations[var_name] = Any
                    
            namespace['__annotations__'] = annotations
            
        return super().__new__(mcs, name, bases, namespace, **kwargs)

    
def dummy_func():
    pass
    
class MyBaseModel(BaseModel, metaclass=MyModelMetaclass):
    # Pydantic does not know how to ignore Cython functions, so we have to configure that explicitly
    
    class Config:
        arbitrary_types_allowed = True
        keep_untouched = (type(dummy_func),)

# -------------------- END OF CYTHON WORKAROUND --------------------


class LayerConnection(MyBaseModel):
    src_id: str = ''
    src_var: str = ''
    dst_id: str = ''
    dst_var: str = ''

    class Config:
        allow_mutation = False
        
    def __hash__(self):
        return hash(self.src_id + self.src_var + self.dst_id + self.dst_var)
    
    
class LayerSpec(ABC, MyBaseModel):
    id_: str = ''
    name: str = ''
    type_: str = ''
    backward_connections: Tuple[LayerConnection, ...] = ()
    forward_connections: Tuple[LayerConnection, ...] = ()
    visited: bool = False
    custom_code: Union[str, None] = None
    checkpoint_path: Union[str, None] = None    
    end_points: Union[Tuple[str, ...], None] = None

    class Config:
        allow_mutation = False
        
    def clone(self, modified_params: Dict[str, Any]=None) -> 'LayerSpec':
        modified_params = modified_params or {}
        params = {}
        for key in self.fields.keys():
            params[key] = getattr(self, key)

        params.update(modified_params)
        return self.__class__(**params)

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
            'end_points': tuple(dict_.get('endPoints', ())),
            'checkpoint_path': cls.resolve_checkpoint_path(dict_),
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
        dict_['endPoints'] = list(self.end_points)

        if self.checkpoint_path is None:
            dict_['checkpoint'] = []
        else:
            dict_['checkpoint'] = {'1': os.path.join(self.checkpoint_path, 'dummy.ckpt')} # TODO: hack to make it work with mysterious frontend behavior. Ask for refactor when this causes trouble.

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
        return self.type_ + sanitize_name(self.name)

    def __repr__(self):
        return f"{self.__class__.__name__} (name: {self.name}, id: {self.id_}, type: {self.type_})"
        
    @classmethod
    def resolve_checkpoint_path(cls, dict_):
        import platform
        
        if 'checkpoint' not in dict_ or len(dict_['checkpoint']) == 0:
            return None
        
        ckpt_path = dict_['checkpoint']['1']
        if '//' in ckpt_path:
            if platform.system() == 'Windows':
                new_ckpt_path = ckpt_path.split('//')[1]
            else:
                new_ckpt_path = os.path.sep+ckpt_path.split(2*os.path.sep)[1] # Sometimes frontend repeats the directory path. /<dir-path>//<dir-path>/model.ckpt-1
                logger.warning(
                    f"Splitting malformed checkpoint path: '{ckpt_path}'. "
                    f"New path: '{new_ckpt_path}'"
                )
                ckpt_path = new_ckpt_path
                
        ckpt_path = os.path.dirname(ckpt_path)
        ckpt_path = ckpt_path.replace('\\','/')
        return ckpt_path        
    
        
        
        
'''

class LayerSpec(ABC):
    Connection = namedtuple('Connection', ['src_id', 'src_var', 'dst_id', 'dst_var'])
    
    _base_parameters = [
        ParamSpec('id_', str, None, 'A unique identifier', required=True),
        ParamSpec('name', str, None, 'A unique name', required=True),
        ParamSpec('type_', str, None, 'A type identifier', required=True),
        ParamSpec('visited', bool, False, 'Whether this layer has been explicitly modified by the user', required=False),        
        ParamSpec('custom_code', (str, type(None)), None, 'A code version of this layer. Will override other settings', required=False),
        ParamSpec('backward_connections', tuple, tuple, 'A list of layer ids pointing to this node', required=False),
        ParamSpec('forward_connections', tuple, tuple, 'A list of layer ids pointed to by this node', required=False),
        ParamSpec('checkpoint_path', (str, type(None)), None, 'A path where checkpoint information can be found', required=False),
        ParamSpec('end_points', (tuple), tuple, '?', required=False)                                
    ]


    def __init__(self, **kwargs):
        def get_default(param_spec):
            if callable(param.default):
                return param.default()
            else:
                return param.default

        # Check that all required args are present. Set default values for missing non-requireds and for type mismatches.        
        for param in self.parameter_specs:
            if param.name not in kwargs:
                if param.required:
                    raise RuntimeError(f"Layer '{type(self).__name__}', parameter '{param.name}': parameter is required but not present")
                else:
                    kwargs[param.name] = get_default(param)
                    logger.debug(f"Layer '{type(self).__name__}', parameter '{param.name}': parameter is not present. Using default value: {param.default}")
            else:
                value = kwargs[param.name]
                if not isinstance(value, param.valid_types):
                    kwargs[param.name] = get_default(param)
                    if isinstance(param.valid_types, tuple):
                        valid_types_str = "one of " + "".join(f"'{t.__name__}'" for t in param.valid_types)
                    else:
                        valid_types_str = f"'{param.valid_types.__name__}'"
                    logger.warning(f"Layer '{type(self).__name__}', parameter '{param.name}': got type '{type(value)}', expected {valid_types_str}. Using default value: {param.default}")
                    print('value', value)

        expected_params = set([p.name for p in self.parameter_specs])
        for key, value in kwargs.items():
            if hasattr(self, key):
                raise RuntimeError(f"Parameter '{key}' would overwrite existing property!")

            if key in expected_params:
                setattr(self, key, value)
            else:
                logger.info(f"Unexpected parameter '{key}' in spec of type '{type(self)}'. This parameter will be ignored.")
            
    @property
    @abstractmethod
    def _parameters(self) -> List[ParamSpec]:
        raise NotImplementedError

    @property
    def parameter_specs(self) -> List[ParamSpec]:
        return self._base_parameters + self._parameters
    
    @property
    def sanitized_name(self) -> str:
        """ Name with spaces replaced by underscore, as well as a prepended underscore. Prepended layer type """
        return self.type_ + sanitize_name(self.name)

    def __repr__(self):
        return f"{self.__class__.__name__} (name: {self.name}, id: {self.id_}, type: {self.type_})"

    
class LayerSpecBuilder(ABC):
    @property
    @abstractmethod    
    def target_class(self) -> Type[LayerSpec]:
        raise NotImplementedError

    def from_kwargs(self, **kwargs: Dict[str, Any]) -> 'LayerSpecBuilder':
        for key, value in kwargs.items():
            self.set_parameter(key, value)
        return self

    def from_existing(self, existing: LayerSpec) -> 'LayerSpecBuilder':
        for param_spec in existing.parameter_specs:
            param_value = getattr(existing, param_spec.name)
            self.set_parameter(param_spec.name, param_value)
        return self

    def from_dict_base(self, id_, dict_: Dict):
        self.set_parameter('id_', id_)
        self.set_parameter('name', dict_['Name'])
        self.set_parameter('type_', dict_['Type'])
        self.set_parameter('visited', dict_.get('Visited', False))        
        self.set_parameter('end_points', tuple(dict_.get('endPoints', ())))
        self.set_parameter('checkpoint_path', self._resolve_checkpoint_path(dict_))

        self.set_parameter(
            'backward_connections',
            tuple(
                LayerSpec.Connection(src_id=conn_spec['src_id'], src_var=conn_spec['src_var'], dst_id=id_, dst_var=conn_spec['dst_var'])
                for conn_spec in dict_['backward_connections']
            )
        )
        self.set_parameter(
            'forward_connections',
            tuple(
                LayerSpec.Connection(src_id=id_, src_var=conn_spec['src_var'], dst_id=conn_spec['dst_id'], dst_var=conn_spec['dst_var'])                
                for conn_spec in dict_['forward_connections']
            )
        )

        
        if dict_['Code'] is not None and 'Output' in dict_['Code']:
            custom_code = dict_['Code']['Output']
        else:
            custom_code = dict_['Code']
            
        if custom_code is not None and custom_code.strip() == '':
            custom_code = None
        self.set_parameter('custom_code', custom_code)        

    def _resolve_checkpoint_path(self, dict_):
        import platform
        
        if 'checkpoint' not in dict_ or len(dict_['checkpoint']) == 0:
            return None
        
        ckpt_path = specs['checkpoint']['1']
        if '//' in ckpt_path:
            if platform.system() == 'Windows':
                new_ckpt_path = ckpt_path.split('//')[1]
            else:
                new_ckpt_path = os.path.sep+ckpt_path.split(2*os.path.sep)[1] # Sometimes frontend repeats the directory path. /<dir-path>//<dir-path>/model.ckpt-1
            logger.warning(
                f"Splitting malformed checkpoint path: '{ckpt_path}'. "
                f"New path: '{new_ckpt_path}'"
            )
            ckpt_path = new_ckpt_path
            
        ckpt_path = os.path.dirname(ckpt_path)
        ckpt_path = ckpt_path.replace('\\','/')
        return ckpt_path        

    @abstractmethod
    def from_dict(self, id_, dict_: Dict) -> 'LayerSpecBuilder':
        """ Creates a layer spec builder with values pre-populated from a 'json network' layer dict """
        raise NotImplementedError

    def to_dict_base(self, existing: LayerSpec) -> Dict:
        """ Deconstructs a layer spec into a 'json network' layer dict """
        dict_ = {}
        dict_['Name'] = existing.name
        dict_['Type'] = existing.type_
        dict_['Code'] = existing.custom_code
        dict_['endPoints'] = list(existing.end_points)

        if existing.checkpoint_path is None:
            dict_['checkpoint'] = []
        else:
            dict_['checkpoint'] = {'1': os.path.join(existing.checkpoint_path, 'dummy.ckpt')} # TODO: hack to make it work with mysterious frontend behavior. Ask for refactor when this causes trouble.

        dict_['backward_connections'] = [
            {
                'src_id': c.src_id,
                'src_var': c.src_var,
                'dst_var': c.dst_var
            }            
            for c in existing.backward_connections
        ]
        dict_['forward_connections'] = [
            {
                'dst_id': c.dst_id,
                'dst_var': c.dst_var,
                'src_var': c.src_var
            }            
            for c in existing.forward_connections
        ]
        return dict_
        
    @abstractmethod
    def to_dict(self, existing: LayerSpec) -> Dict:
        """ Deconstructs a layer spec into a 'json network' layer dict """
        raise NotImplementedError        

    def build(self):
        kwargs = {}
        if hasattr(self, '_assigned_parameters'):
            kwargs.update(self._assigned_parameters)

        text = f"Building target class {self.target_class.__name__} with kwargs:\n"
        for key, value in kwargs.items():
            text += f"    {key}: {value} [{type(value).__name__}]\n"
        logger.debug(text)        
        created = self.target_class(**kwargs)
        return created        

    def set_parameter(self, key: str, value: Any):
        if not hasattr(self, '_assigned_parameters'):
            self._assigned_parameters = {}        
        self._assigned_parameters[key] = value
        return self
'''
        
class DummySpec(LayerSpec):
    pass


"""
class DummyBuilder(LayerSpecBuilder):
    target_class = DummySpec
        
    def from_dict(self, id_: str, dict_: Dict):
        self.from_dict_base(id_, dict_)        
        return self

    def to_dict(self, existing: LayerSpec) -> Dict:
        dict_ = self.to_dict_base(existing)
        return dict_
""" 
