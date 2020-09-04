import os
import logging
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Type, Any, List
from collections import namedtuple

from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


def sanitize_name(name):
    name = name.replace(' ', '_')
    name = '_' + name
    return name


class ParamSpec:
    def __init__(self, name, valid_types, default, description, required=False):
        self.name = name
        self.valid_types = valid_types
        self.default = default
        self.description = description
        self.required = required


class LayerSpec(ABC):
    Connection = namedtuple('Source', ['id', 'name'])
    
    _base_parameters = [
        ParamSpec('id', str, None, 'A unique identifier', required=True),
        ParamSpec('name', str, None, 'A unique name', required=True),
        ParamSpec('type', str, None, 'A type identifier', required=True),
        ParamSpec('visited', bool, False, 'Whether this layer has been explicitly modified by the user', required=True),        
        ParamSpec('code', (str, type(None)), None, 'A code version of this layer. Will override other settings', required=True),
        ParamSpec('backward_connections', tuple, tuple, 'A list of layer ids pointing to this node', required=True),
        ParamSpec('forward_connections', tuple, tuple, 'A list of layer ids pointed to by this node', required=True),
        ParamSpec('checkpoint_path', (str, type(None)), str, 'A path where checkpoint information can be found', required=True),
        ParamSpec('end_points', (tuple), tuple, '?', required=True)                                
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
        """ Name with spaces replaced by underscore, as well as a prepended underscore """
        return sanitize_name(self.name)

    def __repr__(self):
        return f"{self.__class__.__name__} (name: {self.name}, id: {self.id}, type: {self.type})"


class LayerSpecBuilder(ABC):
    @property
    @abstractmethod    
    def target_class(self) -> Type[LayerSpec]:
        raise NotImplementedError

    def from_existing(self, existing: LayerSpec) -> 'LayerSpecBuilder':
        for param_spec in existing.parameter_specs:
            param_value = getattr(existing, param_spec.name)
            self.set_parameter(param_spec.name, param_value)
        return self

    def from_dict_base(self, id_, dict_: Dict):
        self.set_parameter('id', id_)
        self.set_parameter('name', dict_['Name'])
        self.set_parameter('type', dict_['Type'])
        self.set_parameter('code', dict_['Code'])
        self.set_parameter('visited', dict_.get('Visited', False))        
        self.set_parameter('end_points', tuple(dict_.get('endPoints', ())))
        self.set_parameter('checkpoint_path', self._resolve_checkpoint_path(dict_))
        self.set_parameter('backward_connections', tuple(LayerSpec.Connection(id_, name) for id_, name in dict_['backward_connections']))
        self.set_parameter('forward_connections', tuple(LayerSpec.Connection(id_, name) for id_, name in dict_['forward_connections']))                

    def _resolve_checkpoint_path(self, dict_):
        import platform
        
        if len(dict_['checkpoint']) == 0:
            return None
        
        ckpt_path = dict_['checkpoint'][1]
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
        dict_['Type'] = existing.type
        dict_['Code'] = existing.code
        dict_['endPoints'] = list(existing.end_points)

        if existing.checkpoint_path is None:
            dict_['checkpoint'] = []
        else:
            dict_['checkpoint'] = {'1': os.path.join(existing.checkpoint_path, 'dummy.ckpt')} # TODO: hack to make it work with mysterious frontend behavior. Ask for refactor when this causes trouble.

        dict_['backward_connections'] = [[c.id, c.name] for c in existing.backward_connections]
        dict_['forward_connections'] = [[c.id, c.name] for c in existing.forward_connections]
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

        
class DummySpec(LayerSpec):
    _parameters = []


class DummyBuilder(LayerSpecBuilder):
    target_class = DummySpec
        
    def from_dict(self, id_: str, dict_: Dict):
        self.from_dict_base(id_, dict_)        
        return self

    def to_dict(self, existing: LayerSpec) -> Dict:
        dict_ = self.to_dict_base(existing)
        return dict_
    
