import os
import copy
import pprint
import re
import json
import ast
import copy
import logging
import pkg_resources
from typing import Dict

from perceptilabs.utils import stringify
from perceptilabs.utils import add_line_numbering
from perceptilabs.core_new.graph import Graph
from perceptilabs.core_new.layers.templates import J2Engine
from perceptilabs.core_new.graph.utils import sanitize_layer_name
from perceptilabs.layers.utils import get_layer_definition
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.core_new.layers.definitions import TEMPLATES_DIRECTORY


TOP_LEVEL_IMPORTS = {
    'standard_library': [
        'import os',        
        'import sys',
        'import logging',
        'from typing import Dict, List, Generator',                
    ],
    'third_party': [
    ],
    'perceptilabs': [
        'from perceptilabs.core_new.graph.builder import GraphBuilder, SnapshotBuilder',
        'from perceptilabs.core_new.communication import TrainingServer',
        'from perceptilabs.messaging import ZmqMessagingFactory, SimpleMessagingFactory',
        'from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP, REPLICATED_PROPERTIES_TABLE'                    
    ]
}

logger = logging.getLogger(APPLICATION_LOGGER)


class ScriptBuildError(Exception):
    pass

def is_syntax_ok(code):
    try:
        ast.parse(code)
    except SyntaxError as e:
        return False
    else:
        return True

    
class FetchParameterError(ScriptBuildError):
    def __init__(self, layer_id, layer_name, layer_type, parameter):
        self.parameter = parameter
        self.layer_id = layer_id
        self.layer_name = layer_name
        self.layer_type = layer_type


def is_syntax_ok(code):
    try:
        ast.parse(code)
    except SyntaxError as e:
        return False
    else:
        return True


class ScriptFactory:
    def __init__(self, mode='tf1x', max_time_run=None, simple_message_bus=False, running_mode = 'initializing'):

        self._mode = mode
        
        self._simple_message_bus = simple_message_bus
        
        templates_directory = pkg_resources.resource_filename('perceptilabs', TEMPLATES_DIRECTORY)
        self._engine = J2Engine(templates_directory)
        self._top_level_imports = TOP_LEVEL_IMPORTS
        self._max_time_run = max_time_run
        self._running_mode = running_mode
        
    def get_runscript(self, graph_spec):
        code  = self._create_graph_snippet(graph_spec)
        code += "\n"
        code += "iterator = graph.training_nodes[0].layer_instance.run(graph)\n"
        code += "result = None\n"
        code += "sentinel = object()\n"        
        code += "while result is not sentinel:\n"
        code += "    result = next(iterator, sentinel)\n"        
        return code

    def get_imports(self, graph_spec):
        code = self._create_imports_snippet(graph_spec)
        code += self._create_logging_snippet()
        return code

    def get_layer_import_statements(self, layer_spec, include_top_level=False):
        if include_top_level:
            standard_library_imports = set(self._top_level_imports['standard_library'])
            third_party_imports = set(self._top_level_imports['third_party'])       
            perceptilabs_imports = set(self._top_level_imports['perceptilabs'])
        else:
            standard_library_imports = set()
            third_party_imports = set()
            perceptilabs_imports = set()

        def add_to_set(from_list, target_set):
            for stmt in from_list:
                if not is_syntax_ok(stmt):
                    raise ScriptBuildError(f"Invalid syntax for import statement '{stmt}' found in layer def for {layer_spec.layer_type}")
                target_set.add(stmt)


        layer_def = get_layer_definition(layer_spec.type_, tf2x=(self._mode=='tf2x'))
        if layer_def is None:
            raise RuntimeError(f"No layer definition for '{layer_spec.type_}'. Check perceptilabs.layers.definitions module")
        
        package_root = pkg_resources.resource_filename('perceptilabs', '.')
        _imports_path = os.path.join(package_root, layer_def.imports_path)
        
        if os.path.isfile(_imports_path):
            imports_path = _imports_path
        else:
            raise ValueError(f"Couldn't locate imports file {_imports_path}. Used directory '.' and '{package_root}'")        
        
        with open(imports_path, 'r') as f:
            try:
                imports_dict = json.load(f)
            except:
                logger.exception(f"Error when opening imports file at {imports_path}. Layer: {layer_spec}")
                raise

        add_to_set(imports_dict['standard_library'], standard_library_imports)
        add_to_set(imports_dict['perceptilabs'], perceptilabs_imports)
        add_to_set(imports_dict['third_party'], third_party_imports)

        return standard_library_imports, third_party_imports, perceptilabs_imports                
    
    def _create_imports_snippet(self, graph):
        standard_library_imports = set(self._top_level_imports['standard_library'])
        third_party_imports = set(self._top_level_imports['third_party'])       
        perceptilabs_imports = set(self._top_level_imports['perceptilabs'])

        for node in graph.nodes_by_id.values():
            stdlib, thirdparty, plabs = self.get_layer_import_statements(node)
            standard_library_imports.update(stdlib)
            third_party_imports.update(thirdparty)
            perceptilabs_imports.update(plabs)

        code = ''
        for stmt in sorted(standard_library_imports, key=len):
            code += stmt + '\n'
        if len(code) > 0:
            code += '\n'

        for stmt in sorted(third_party_imports, key=len):
            code += stmt + '\n'
        if len(code) > 0:
            code += '\n'

        for stmt in sorted(perceptilabs_imports, key=len):
            code += stmt + '\n'            
        if len(code) > 0:
            code += '\n'

        return code
    
    def _create_layers_snippet(self, graph_spec, offset=None):
        code = ''
        line_to_node_map = {} if offset is not None else None
        
        for layer_spec in graph_spec.nodes_by_id.values():
            layer_code = self.render_layer_code(
                layer_spec, macro_kwargs={'graph_spec': graph_spec, 'layer_spec': layer_spec}
            )
            code += layer_code + '\n'
            n_lines = len(layer_code.split('\n'))

            if offset is not None:
                line_to_node_map.update({offset+line: (layer_spec, line) for line in range(n_lines)})
                offset += n_lines

        if len(code) > 0:
            code += '\n'
        return code, line_to_node_map
    
    def _create_logging_snippet(self):
        code  = "logging.basicConfig(\n"
        code += "    stream=sys.stdout,\n"
        code += "    format='%(asctime)s - %(levelname)s - %(message)s',\n"
        code += "    level=logging.INFO\n"
        code += ")\n"
        code += "log = logging.getLogger(__name__)\n\n"
        return code        
    
    def _create_graph_snippet(self, graph_spec):
        code = "layer_classes = {\n"
        for node in graph_spec.nodes_by_id.values():
            code += "    '" + node.sanitized_name + "': " + node.sanitized_name + ",\n"
        code += "}\n\n"

        code += "edges = {\n"
        for node in graph_spec.nodes_by_id.values():
            src_name = node.sanitized_name
            for conn_spec in node.forward_connections:
                dst_name = graph_spec.nodes_by_id[conn_spec.dst_id].sanitized_name
                code += "    ('" + src_name + "', '" + dst_name + "'),\n"
        code += "}\n\n"


        # TODO(anton.k): remove this when refactoring....

        mapping = {}
        for src_node in graph_spec.nodes_by_id.values():
            
            for conn_spec in src_node.forward_connections:
                dst_node = graph_spec.nodes_by_id[conn_spec.dst_id]
                key = src_node.sanitized_name + ':' + dst_node.sanitized_name
                if not key in mapping:
                    mapping[key] = []
                mapping[key].append((conn_spec.src_var, conn_spec.dst_var))
                
        code += "conn_info = {\n"
        for key, value in mapping.items():
            code += "    '{}': {},\n".format(key, value)
        code += "}\n\n"
        # --------------

        return code

    def _create_training_server_snippet(self, topic_generic, topic_snapshots, userland_timeout):
        code  = "snapshot_builder = SnapshotBuilder(\n"
        code += "    BASE_TO_REPLICA_MAP, \n"
        code += "    REPLICATED_PROPERTIES_TABLE\n"
        code += ")\n"
        code += "\n"        
        code += "topic_generic = {}\n".format(topic_generic)
        code += "topic_snapshots = {}\n".format(topic_snapshots)

        if self._simple_message_bus:
            code += "factory = SimpleMessagingFactory()\n"            
        else:
            code += "factory = ZmqMessagingFactory()\n"
            
        code += "producer_generic = factory.make_producer(topic_generic)\n"
        code += "producer_snapshots = factory.make_producer(topic_snapshots)\n"
        code += "consumer = factory.make_consumer([topic_generic])\n"
        code += "\n"
        code += "graph_builder = GraphBuilder()\n"
        code += "\n"        
        code += "server = TrainingServer(\n"
        code += "    producer_generic, producer_snapshots, consumer,\n"
        code += "    graph_builder,\n"
        code += "    layer_classes,\n"
        code += "    edges,\n"
        code += "    conn_info,\n" 
        code += "    mode = '{}',\n".format(self._running_mode)                       
        code += "    snapshot_builder=snapshot_builder,\n"
        code += "    userland_timeout={},\n".format(userland_timeout)
        if self._max_time_run is not None:
            code += "    max_time_run={},\n".format(self._max_time_run) # For debugging
        code += "    userland_logger=log\n"
        code += ")\n\n"

        return code

    def _create_main_block(self):
        code  = "def main(auto_start=False):\n"
        code += "    server.run(auto_start=auto_start)\n"
        code += "\n"
        code += "if __name__ == '__main__':\n"
        #code += "    wait = '--wait' in sys.argv\n"
        code += "    main(auto_start=True)\n"
        
        return code

    def make(self, graph_spec, session_id, topic_generic, topic_snapshots, userland_timeout=15):
        code  = self._create_imports_snippet(graph_spec)
        code += self._create_logging_snippet()
        
        # Add the layer classes
        initial_offset = len(code.split('\n')) - 1
        layers_code, line_to_node_map = self._create_layers_snippet(graph_spec, initial_offset)
        code += layers_code

        code += self._create_graph_snippet(graph_spec)
        code += self._create_training_server_snippet(topic_generic, topic_snapshots, userland_timeout)
        code += self._create_main_block()
        return code, line_to_node_map

    def render_layer_code(self, layer_spec, macro_kwargs=None):
        if layer_spec.custom_code is not None:
            return layer_spec.custom_code
        else:
            # TODO(anton.k): exact path defined in layerspec instead?
            package_root = pkg_resources.resource_filename('perceptilabs', '.')
            layer_def = get_layer_definition(layer_spec.type_, tf2x=(self._mode=='tf2x'))
            if layer_def is None:
                raise RuntimeError(f"No layer definition for '{layer_spec.type_}'. Check perceptilabs.layers.definitions module")
            
            _macro_path = os.path.join(package_root, layer_def.macro_path)

            if os.path.isfile(_macro_path):
                macro_path = _macro_path
            else:
                raise ValueError(f"Couldn't locate macro {_macro_path}. Used directory '.' and '{package_root}'")        
            
            with open(macro_path, 'r') as f:
                template = f.read()
                template += "\n\n"

            macro_kwargs = macro_kwargs or {}
            args_str = ', '.join(f'{name}={name}' for name in macro_kwargs.keys())            
            template += "{{" + f"{layer_def.macro_name}({args_str})" + "}}\n"

            try:
                code = self._engine.render_string(template, **macro_kwargs).strip()
            except:
                logger.exception(f"Error when rendering jinja macro {layer_def.macro_path}:{layer_def.macro_name}. Contents :\n" + add_line_numbering(template))
                raise

            return code
    
        
    
        
        
if __name__ == "__main__":
    from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP
    from perceptilabs.core_new.graph.builder import GraphBuilder
    from perceptilabs.core_new.graph import Graph
    import json

    with open('net.json_', 'r') as f:
        graph_spec = json.load(f)
    
    script_factory = ScriptFactory()
    graph_builder = GraphBuilder()    

    graph = graph_builder.build_from_spec(graph_spec)

    import_code = script_factory.get_imports(graph)
    layer_code, _ = script_factory._create_layers_snippet(graph)    
    run_code = script_factory.get_runscript(graph)    


    code  = import_code
    code += layer_code
    code += run_code


    with open('test_code.py', 'w') as f:
        f.write(code)
        
    
    

    
