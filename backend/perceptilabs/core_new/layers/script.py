import os
import copy
import pprint
import re
import ast
import copy
import logging
import pkg_resources
from typing import Dict

from perceptilabs.utils import add_line_numbering
from perceptilabs.core_new.graph import Graph
from perceptilabs.core_new.layers.templates import J2Engine
from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE, TEMPLATES_DIRECTORY, TOP_LEVEL_IMPORTS
from perceptilabs.core_new.graph.utils import sanitize_layer_name

# TODO: move this to a more suitable location? Deployment?

log = logging.getLogger(__name__)


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
    pass


def is_syntax_ok(code):
    try:
        ast.parse(code)
    except SyntaxError as e:
        return False
    else:
        return True


class ScriptFactory:
    def __init__(self, mode='default', max_time_run=None):
        # if legacy, simply reuse codehq
        # if modern, use modern when possible if not try to wrap hq layers

        templates_directory = pkg_resources.resource_filename('perceptilabs', TEMPLATES_DIRECTORY)
        self._engine = J2Engine(templates_directory)
        self._definition_table = DEFINITION_TABLE
        self._top_level_imports = TOP_LEVEL_IMPORTS
        self._max_time_run = max_time_run
        
    def get_runscript(self, graph: Graph):
        code  = self._create_graph_snippet(graph)
        code += "\n"
        code += "iterator = graph.training_nodes[0].layer_instance.run(graph)\n"
        code += "result = None\n"
        code += "sentinel = object()\n"        
        code += "while result is not sentinel:\n"
        code += "    result = next(iterator, sentinel)\n"        
        return code

    def get_imports(self, graph: Graph):
        code = self._create_imports_snippet(graph)
        code += self._create_logging_snippet()
        return code

    def _create_imports_snippet(self, graph):
        plabs_imports = set(self._top_level_imports['perceptilabs'])
        other_imports = set(self._top_level_imports['standard_library'] + self._top_level_imports['third_party'])
        
        for node in graph.nodes:
            layer_def = self._definition_table.get(node.layer_type)
            
            for stmt in layer_def.import_statements:
                if not is_syntax_ok(stmt):
                    raise ScriptBuildError(f"Invalid syntax for import statement '{stmt}' found in layer def for {node.layer_type}")


                # TODO: the import_statements property should do this distinction (and into third party as well to comply with pep8)
                if 'perceptilabs' in stmt:
                    plabs_imports.add(stmt)
                else:
                    other_imports.add(stmt)

        code = ''        
        for stmt in sorted(other_imports, key=len):
            code += stmt + '\n'
        if len(code) > 0:
            code += '\n'
            
        for stmt in sorted(plabs_imports, key=len):
            code += stmt + '\n'            
        if len(code) > 0:
            code += '\n'
        return code

    def _create_logging_snippet(self):
        code  = "logging.basicConfig(\n"
        code += "    stream=sys.stdout,\n"
        code += "    format='%(asctime)s - %(levelname)s - %(message)s',\n"
        code += "    level=logging.INFO\n"
        code += ")\n"
        code += "log = logging.getLogger(__name__)\n\n"
        return code        
    
    def _create_layers_snippet(self, graph, offset=None):
        code = ''
        line_to_node_map = {} if offset is not None else None
        
        for node in graph.nodes:
            layer_code = self.render_layer_code(
                node.layer_id,
                node.layer_type,
                node.layer_spec,
                node.custom_code
            )
            code += layer_code + '\n'
            n_lines = len(layer_code.split('\n'))
            
            if offset is not None:
                line_to_node_map.update({offset+line: (node, line) for line in range(n_lines)})
                offset += n_lines

        if len(code) > 0:
            code += '\n'
        return code, line_to_node_map

    def _create_graph_snippet(self, graph):
        code = "layers = {\n"
        for node in graph.nodes:
            layer_name = node.layer_type + node.layer_id
            code += "    '" + node.layer_id + "': " + layer_name + "(),\n"
        code += "}\n\n"

        code += "edges = {\n"
        for node in graph.nodes:
            from_id = node.layer_id
            for _, to_id in node.layer_spec['forward_connections']:
                code += "    ('" + from_id + "', '" + sanitize_layer_name(to_id) + "'),\n"
        code += "}\n\n"

        code += "graph_builder = GraphBuilder()\n"
        code += "graph = graph_builder.build(layers, edges)\n\n"        
        return code

    def _create_training_server_snippet(self, port1, port2, userland_timeout):
        # TODO: ...        
        return ""

    def _create_rest_server_snippet(self):
        # TODO: a rest endpoint that provides metrics by reading from the TrainingServer
        return ""

    def _create_logging_snippet(self):
        code  = "logging.basicConfig(\n"
        code += "    stream=sys.stdout,\n"
        code += "    format='%(asctime)s - %(levelname)s - %(message)s',\n"
        code += "    level=logging.INFO\n"
        code += ")\n"
        code += "log = logging.getLogger(__name__)\n\n"
        return code        
    
    def _create_layers_snippet(self, graph, offset):
        code = ''
        line_to_node_map = {}
        
        for node in graph.nodes:
            layer_code = self.render_layer_code(
                node.layer_id,
                node.layer_type,
                node.layer_spec,
                node.custom_code
            )
            code += layer_code + '\n'
            n_lines = len(layer_code.split('\n'))
            line_to_node_map.update({offset+line: (node, line) for line in range(n_lines)})
            offset += n_lines

        if len(code) > 0:
            code += '\n'
        return code, line_to_node_map

    def _create_graph_snippet(self, graph):
        code = "layers = {\n"
        for node in graph.nodes:
            layer_name = node.layer_type + node.layer_id
            code += "    '" + node.layer_id + "': " + layer_name + "(),\n"
        code += "}\n\n"

        code += "edges = {\n"
        for node in graph.nodes:
            from_id = node.layer_id
            for _, to_id in node.layer_spec['forward_connections']:
                code += "    ('" + from_id + "', '" + sanitize_layer_name(to_id) + "'),\n"
        code += "}\n\n"

        code += "graph_builder = GraphBuilder()\n"
        code += "graph = graph_builder.build(layers, edges)\n\n"        
        return code

    def _create_training_server_snippet(self, topic_generic, topic_snapshots, userland_timeout):
        code  = "snapshot_builder = SnapshotBuilder(\n"
        code += "    BASE_TO_REPLICA_MAP, \n"
        code += "    REPLICATED_PROPERTIES_TABLE\n"
        code += ")\n"
        code += "\n"        
        code += "topic_generic = {}\n".format(topic_generic)
        code += "topic_snapshots = {}\n".format(topic_snapshots)
        code += "producer_generic = ZmqMessageProducer(topic_generic)\n"
        code += "producer_snapshots = ZmqMessageProducer(topic_snapshots)\n"
        code += "consumer = ZmqMessageConsumer([topic_generic])\n"
        code += "\n"
        code += "server = TrainingServer(\n"
        code += "    producer_generic, producer_snapshots, consumer,\n"
        code += "    graph,\n"
        code += "    snapshot_builder=snapshot_builder,\n"
        code += "    userland_timeout={},\n".format(userland_timeout)
        if self._max_time_run is not None:
            code += "    max_time_run={},\n".format(self._max_time_run) # For debugging
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

    def make(self, graph, session_id, topic_generic, topic_snapshots, userland_timeout=15):
        code  = self._create_imports_snippet(graph)
        code += self._create_logging_snippet()
        
        # Add the layer classes
        initial_offset = len(code.split('\n')) - 1
        layers_code, line_to_node_map = self._create_layers_snippet(graph, initial_offset)
        code += layers_code

        code += self._create_graph_snippet(graph)
        code += self._create_training_server_snippet(topic_generic, topic_snapshots, userland_timeout)
        code += self._create_rest_server_snippet()
        code += self._create_main_block()
        return code, line_to_node_map

    def render_layer_code(self, layer_id, layer_type, layer_spec, custom_code=None):
        if custom_code is not None:
            code = custom_code
        else:
            code = self._render_layer_macro(layer_id, layer_type, layer_spec)
        return code
    
    def _render_layer_macro(self, layer_id, layer_type, layer_spec):
        """ Creates a Jinja2 template that imports the layer macro and renders it """
        def_ = self._definition_table.get(layer_type)

        if def_ is None:
            raise ScriptBuildError(f"No layer definition found for layer of type '{layer_type}'")
        layer_name = layer_type + layer_id

        kwargs = self._fetch_parameters(layer_spec, def_.macro_parameters)
        kwargs['layer_name'] = "'" + layer_name + "'"
        arg_str = ', '.join(f"{k}={v}" for k, v in kwargs.items())
        
        template  = "{% from '" + def_.template_file + "' import " + def_.template_macro + " %}\n"
        template += "{{ " + def_.template_macro + "(" + arg_str + ")}}"

        log.debug(
            f"Created macro loader for layer {layer_id} [{layer_type}]:\n"
            f"---------\n"            
            f"{add_line_numbering(template)}\n"
            f"---------\n"            
            f"kwargs: {repr(kwargs)}.\n"
        )

        try:
            code = self._engine.render_string(template)
        except:
            file_contents = open(os.path.join(self._engine.templates_directory, def_.template_file)).read()            
            log.exception(f"Error when rendering jinja macro {def_.template_file}:{def_.template_macro}. Contents :\n" + add_line_numbering(file_contents))
            raise


        #print("code", add_line_numbering(code))
        #import pdb; pdb.set_trace()
        
        return code    
        
    def _fetch_parameters(self, layer_spec, macro_parameters):
        results = {}
        
        for key, value in macro_parameters.items():
            if key == 'layer_name':
                # Reserved. Always present.
                raise ScriptBuildError("Cannot use reserved name 'layer_name' for macro parameter")

            if callable(value):
                try:
                    value = value(layer_spec)
                except Exception as e:
                    raise FetchParameterError(f"Failed to fetch parameter '{key}'") from e
            value = copy.deepcopy(value)
            
            if isinstance(value, str):
                value = f"'{value}'"
            results[key] = value
            
            #import pprint
            #print('FETCH PARAMETERS', pprint.pformat(layer_spec), value) 
            

        return results
    
        
        
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
        
    
    

    
