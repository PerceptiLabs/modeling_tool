import copy
from typing import Dict

from code.templating import J2Engine
from core_new.graph import Graph
from core_new.layers.definitions import DEFINITION_TABLE

class ScriptFactory:
    def __init__(self, mode='default'):
        # if legacy, simply reuse codehq
        # if modern, use modern when possible if not try to wrap hq layers

        self._engine = J2Engine('./code/templates/')

    def make(self, graph: Graph, session_config: Dict[str, str]):
        imports = {}
        macro_calls = []

        for node in graph.nodes:
            layer_type = node.layer_type
            layer_name = layer_type + node.layer_id            
            layer_def = DEFINITION_TABLE.get(layer_type)
            
            if layer_def.template_file not in imports:
                imports[layer_def.template_file] = []
            imports[layer_def.template_file].append(layer_def.template_macro)

            kwargs = self._fetch_parameters(node.layer_spec, layer_def.macro_parameters)
            macro_calls.append((layer_def.template_macro, layer_name, kwargs))

        # TODO: IMPORT MACROS ACCORDING TO THIS INSTEAD OF USING STRINGS http://codyaray.com/2015/05/auto-load-jinja2-macros

        # --- IMPORT LAYER MACROS ---
        template  = ''
        for file_name, macro_names in imports.items():
            macros = ', '.join(macro_names)
            template += "{% from '" + file_name + "' import " + macros + " %}\n"

        template += 'import tensorflow as tf\n'
        template += 'import numpy as np\n'
        template += 'import dill\n'        
        template += 'from core_new.layers import *\n'
        template += 'from core_new.graph import Graph\n'
        template += 'from core_new.graph.builder import GraphBuilder\n'                
        template += 'from core_new.api.mapping import MapServer, ByteMap\n'

        
        # --- CALL LAYER MACROS ---
        template += '\n\n'
        for macro_call in macro_calls:
            macro_name = macro_call[0]
            layer_name = macro_call[1]

            kwargs = macro_call[2]
            kwargs['layer_name'] = "'"+layer_name+"'"
            
            arg_str = ', '.join(f"{k}={v}" for k, v in kwargs.items())
            template += "{{ " + macro_name + "(" + arg_str + ")}}\n\n"

        template += "LAYERS = {\n"
        for node in graph.nodes:
            layer_name = node.layer_type + node.layer_id
            template += "    '" + node.layer_id + "': " + layer_name + "(),\n"
        template += "}\n\n"

        template += "EDGES = {\n"
        for node in graph.nodes:
            from_id = node.layer_id
            for to_id in node.layer_spec['forward_connections']:
                template += "    ('" + from_id + "', '" + to_id + "'),\n"
        template += "}\n\n"

        template += "server = MapServer(\n"
        template += "    'tcp://*:5556',\n"
        template += "    'tcp://*:5557',\n"
        template += "    'tcp://*:5558'\n"        
        template += ")\n\n"
        template += "server.start()\n\n"
        
        template += "state_map = ByteMap(\n"
        template += "    '" + session_config['session_id'] + "',\n"
        template += "    'tcp://localhost:5556',\n"
        template += "    'tcp://localhost:5557',\n"
        template += "    'tcp://localhost:5558'\n"        
        template += ")\n\n"
        template += "state_map.start()\n\n"        
        
        template += "def synchronize_replicas(graph):\n"
        template += "    for node in graph.nodes:\n"
        template += "        l = node.layer\n"
        template += "        lid = node.layer_id\n"        
        template += "        if isinstance(l, Tf1xClassificationLayer):\n"
        template += "            state_map[(lid + '-sample').encode()] = dill.dumps(l.sample)\n"
        template += "            state_map[(lid + '-size_training').encode()] = dill.dumps(l.size_training)\n"
        template += "            state_map[(lid + '-size_validation').encode()] = dill.dumps(l.size_validation)\n"
        template += "            state_map[(lid + '-size_testing').encode()] = dill.dumps(l.size_testing)\n"
        template += "            state_map[(lid + '-variables').encode()] = dill.dumps(l.variables)\n"
        template += "            state_map[(lid + '-accuracy_training').encode()] = dill.dumps(l.accuracy_training)\n"
        template += "            state_map[(lid + '-accuracy_validation').encode()] = dill.dumps(l.accuracy_validation)\n"        
        template += "            state_map[(lid + '-accuracy_testing').encode()] = dill.dumps(l.accuracy_testing)\n"
        template += "            state_map[(lid + '-loss_training').encode()] = dill.dumps(l.loss_training)\n"
        template += "            state_map[(lid + '-loss_validation').encode()] = dill.dumps(l.loss_validation)\n"
        template += "            state_map[(lid + '-loss_testing').encode()] = dill.dumps(l.loss_testing)\n"
        template += "        elif isinstance(l, DataLayer):\n"
        template += "            state_map[(lid + '-sample').encode()] = dill.dumps(l.sample)\n"
        template += "            state_map[(lid + '-size_training').encode()] = dill.dumps(l.size_training)\n"
        template += "            state_map[(lid + '-size_validation').encode()] = dill.dumps(l.size_validation)\n"
        template += "            state_map[(lid + '-size_testing').encode()] = dill.dumps(l.size_testing)\n"
        template += "            state_map[(lid + '-variables').encode()] = dill.dumps(l.variables)\n"
        template += "        elif isinstance(l, Tf1xLayer):\n"
        template += "            state_map[(lid + '-variables').encode()] = dill.dumps(l.variables)\n"
        template += "            state_map[(lid + '-trainable_variables').encode()] = dill.dumps(l.trainable_variables)\n"
        template += "\n\n"
        
        # --- CREATE MAIN FUNCTION ---
        template += 'def main():\n'
        template += '    graph_builder = GraphBuilder()\n'
        template += '    graph = graph_builder.build(LAYERS, EDGES)\n'
        template += '    \n'
        template += '    print(graph.training_nodes)\n'
        template += '    graph.training_nodes[0].layer_instance.send_state_updates = synchronize_replicas\n'
        template += '    graph.training_nodes[0].layer_instance.run(graph)\n'


        print("TEMPLATE ----------")
        for i, l in enumerate(template.split('\n')):
            print(i, l)
        print("ENDTEMPLATE ----------")

        
        #import pdb; pdb.set_trace()
        
        
        code = self._engine.render_string(template)


        
        print("CODE ----------")
        for i, l in enumerate(code.split('\n')):
            print(i, l)
        print("ENDCODE ----------")
        #import pdb; pdb.set_trace()              
        return code

        
    def _fetch_parameters(self, layer_spec, macro_parameters):
        results = {}
        
        for key, value in macro_parameters.items():
            if key == 'layer_name':
                # Reserved. Always present.
                continue
            
            if callable(value):
                value = value(layer_spec)
            value = copy.deepcopy(value)
            
            if isinstance(value, str):
                value = f"'{value}'"
            results[key] = value
            
        return results
    
        


