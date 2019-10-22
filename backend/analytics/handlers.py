import json
from typing import Dict, Any
from collections import namedtuple
from abc import ABC, abstractmethod

Entry = namedtuple('Entry', ['file', 'value'])

class ScraperHandler(ABC):
    @abstractmethod
    def is_applicable(self, meta: Dict[str, Any], values: Dict[str, Any]):
        raise NotImplementedError

    @abstractmethod
    def _apply(self, meta: Dict[str, Any], values: Dict[str, Any]):
        raise NotImplementedError

    def apply(self, meta: Dict[str, Any], values: Dict[str, Any]):
        result = self._apply(meta, values)

        if isinstance(result, Entry):
            return [result]
        if isinstance(result, list) and all([isinstance(x, Entry) for x in result]):            
            return result
        else:
            raise RuntimeError("_apply returned illegal type: {}".format(type(result)))

    def __repr__(self):
        return self.__class__.__name__
    
    
class CubeHandler(ScraperHandler):
    def is_applicable(self, meta: Dict[str, Any], values: Dict[str, Any]):
        return meta.get('tag') == 'cube'

    def _apply(self, meta: Dict[str, Any], values: Dict[str, Any]):
        return Entry('cube.txt', "{}, {}".format(meta['time'], values['x']))

    
class CoreInitHandler(ScraperHandler):
    def is_applicable(self, meta: Dict[str, Any], values: Dict[str, Any]):
        return meta.get('tag') == 'core_init'

    def _apply(self, meta: Dict[str, Any], values: Dict[str, Any]):
        time = meta.get('time')
        graph_dict = values.get('graph_dict', '')

        graph = json.dumps(graph_dict)
        
        result = "{}, {}".format(time, graph)
        return Entry('core_init.txt', result)

    
class CpuAndMemHandler(ScraperHandler):
    def is_applicable(self, meta, values):
        return meta.get('tag') == 'cpu_and_mem'

    def _apply(self, meta, values):
        return Entry(
            'cpu_and_mem.txt',
            '{}, {}, {}'.format(
                meta.get('time'),
                values.get('cpu'),
                values.get('mem')
            )
        )
