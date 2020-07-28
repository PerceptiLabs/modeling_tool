from collections import namedtuple
from typing import Tuple, Dict

from perceptilabs.graph.spec.layers import LayerSpec, LayerSpecBuilder, ParamSpec


class DataDataSpec(LayerSpec):
    Source = namedtuple('Source', ['type', 'path', 'ext', 'split'])

    _parameters = [
        ParamSpec('sources', (tuple,), tuple, 'Tuple of Source objects'),
        ParamSpec('selected_columns', (tuple,), tuple, 'Indices of selected columns'),
        ParamSpec('lazy', (bool,), False, 'Indicates whether data should be loaded lazily or not'),
        ParamSpec('shuffle', (bool,), False, 'Indicates whether data should be shuffled')        
    ]


class DataDataBuilder(LayerSpecBuilder):
    target_class = DataDataSpec
    
    def from_dict(self, id_: str, dict_: Dict):
        self.from_dict_base(id_, dict_)

        if 'Properties' in dict_ and dict_['Properties'] is not None:
            self.set_parameter('selected_columns', tuple(dict_['Properties']['accessProperties']['Columns']))
            self.set_parameter('sources', tuple(self._parse_sources(dict_)))
            
        self.set_parameter('lazy', False)
        self.set_parameter('shuffle', dict_['Properties']['accessProperties']['Shuffle_data'])
        return self
        
    def to_dict(self, existing: LayerSpec) -> Dict:
        dict_ = self.to_dict_base(existing)
        dict_['Properties'] = {
            'accessProperties': {
                'Columns': list(existing.selected_columns),
                'Sources': [{'type': s.type, 'path': s.path} for s in existing.sources],
                'Partition_list': [list(s.split) for s in existing.sources],
                'Shuffle_data': existing.shuffle                
            },
            'lazy': existing.lazy
        }        
        return dict_

    def _parse_sources(self, dict_):
        source_json_list = dict_['Properties']['accessProperties']['Sources']
        partition_json_list = dict_['Properties']['accessProperties']['Partition_list']        

        sources = []
        for source_json, partition_json in zip(source_json_list, partition_json_list):
            source = DataDataSpec.Source(
                type=source_json['type'],
                path=source_json['path'],
                ext=self._resolve_ext_from_path(source_json['type'], source_json['path']),
                split=tuple(partition_json)
            )
            sources.append(source)
        return sources
    
    def _resolve_ext_from_path(self, type_, path):
        import os
        if type_ == 'file':
            ext = os.path.splitext(path)[1]
        elif type_ == 'directory':
            src_exts = [os.path.splitext(x)[1] for x in os.listdir(path)]
            ext = max(set(src_exts), key=src_exts.count) # Most frequent
        else:
            ext = None
        return ext

    
