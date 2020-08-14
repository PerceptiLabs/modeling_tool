import os
from collections import namedtuple
from typing import Tuple, Dict, Any, List, Union
from pydantic import BaseModel, validator

from perceptilabs.layers.specbase import LayerSpec, MyBaseModel


class DataSource(MyBaseModel):
    type_: str = ''
    path: str = ''
    ext: str = ''
    split: Tuple[int, int, int] = (70, 20, 10)

    @validator('path', allow_reuse=True, check_fields=False)
    def remove_path_backslashes(cls, path):
        return path.replace('\\', '/')
    

class DataDataSpec(LayerSpec):
    sources: Tuple[DataSource, ...] = ()
    selected_columns: Union[Tuple[int, ...], None] = None
    lazy: bool = False
    shuffle: bool = False
    type_: str = 'DataData'

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:
            params['selected_columns'] = tuple(dict_['Properties']['accessProperties']['Columns'])
            params['sources'] = tuple(cls._parse_sources(dict_))
            params['lazy'] = False
            params['shuffle'] = dict_['Properties']['accessProperties']['Shuffle_data']
        
        return cls(**params)

    @classmethod
    def _parse_sources(cls, dict_):
        source_json_list = dict_['Properties']['accessProperties']['Sources']
        partition_json_list = dict_['Properties']['accessProperties']['Partition_list']        
    
        sources = []
        for source_json, partition_json in zip(source_json_list, partition_json_list):
            source = DataSource(
                type_=source_json['type'],
                path=source_json['path'],
                ext=cls._resolve_ext_from_path(source_json['type'], source_json['path']),
                split=tuple(partition_json)
            )
            sources.append(source)
        return sources
    
    @classmethod    
    def _resolve_ext_from_path(cls, type_, path):
        import os
        if type_ == 'file':
            ext = os.path.splitext(path)[1]
        elif type_ == 'directory':
            src_exts = [os.path.splitext(x)[1] for x in os.listdir(path)]
            ext = max(set(src_exts), key=src_exts.count) # Most frequent
        else:
            ext = None
        return ext

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:        
        """ Deconstructs a layer spec into a 'json network' layer dict """

        dict_['Properties'] = {
            'accessProperties': {
                'Columns': list(self.selected_columns) if self.selected_columns is not None else None,
                'Sources': [{'type': s.type_, 'path': s.path} for s in self.sources],
                'Partition_list': [list(s.split) for s in self.sources],
                'Shuffle_data': self.shuffle                
            },
            'lazy': self.lazy
        }
        return dict_
        
