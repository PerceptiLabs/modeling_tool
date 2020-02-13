import copy
import ast
import pkg_resources
from typing import Dict

from perceptilabs.core_new.graph import Graph
from perceptilabs.core_new.layers.templates import J2Engine
from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE, TEMPLATES_DIRECTORY
from perceptilabs.core_new.graph.utils import sanitize_layer_name

# TODO: move this to a more suitable location? Deployment?

class ScriptFactory:
    def __init__(self, mode='default'):
        # if legacy, simply reuse codehq
        # if modern, use modern when possible if not try to wrap hq layers

        templates_directory = pkg_resources.resource_filename('perceptilabs', TEMPLATES_DIRECTORY)
        self._engine = J2Engine(templates_directory)

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
        template += 'import zmq\n'        
        template += 'import sys\n'
        template += 'import json\n'
        template += 'import time\n'        
        template += 'import zlib\n'        
        template += 'import logging\n'
        template += 'import threading\n'
        template += 'from typing import Dict, Any, List, Tuple, Generator\n'        
        template += 'from flask import Flask, jsonify\n'#, request\n'
        template += 'import flask'
        template += '\n\n'
        template += 'from perceptilabs.core_new.utils import Picklable\n'
        template += 'from perceptilabs.core_new.communication.status import *\n'        
        template += 'from perceptilabs.core_new.layers import *\n'
        template += 'from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP, REPLICATED_PROPERTIES_TABLE\n'        
        template += 'from perceptilabs.core_new.graph import Graph\n'
        template += 'from perceptilabs.core_new.graph.builder import GraphBuilder, SnapshotBuilder\n'                
        template += 'from perceptilabs.core_new.api.mapping import MapServer, ByteMap\n'
        template += '\n\n'

        template += 'log = logging.getLogger("werkzeug").setLevel(logging.ERROR)\n' #fewer flask messages
        template += 'logging.basicConfig(\n'
        template += '    stream=sys.stdout,\n'
        template += '    format="%(asctime)s - %(levelname)s - %(message)s",\n'
        template += '    level=logging.INFO\n'
        template += ')\n'
        template += 'log = logging.getLogger(__name__)\n'

        template += 'global graph, status, t_start\n'
        template += 'graph = None\n'
        template += 'status = STATUS_INITIALIZING\n'
        template += 't_start = None\n'
        
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
            for _, to_id in node.layer_spec['forward_connections']:
                template += "    ('" + from_id + "', '" + sanitize_layer_name(to_id) + "'),\n"
        template += "}\n\n"

        template += "snapshots = []\n"
        template += "snapshot_lock = threading.Lock()\n"        
        template += "\n"

        template += "context = zmq.Context()\n"
        template += "socket = context.socket(zmq.PUB)\n"
        template += "socket.bind('tcp://*:7171')\n"
        
        template += "app = Flask(__name__)\n"
        template += "app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True\n"
        template += "\n"
        template += "@app.route('/snapshot_count')\n"
        template += "def endpoint_count():\n"
        template += "    return str(len(snapshots))\n"
        
        template += "@app.route('/snapshot')\n"
        template += "def endpoint_snapshot():\n"
        template += "    from flask import request\n"
        template += "    index = int(request.args.get('index'))\n"
        #template += "    if index >= len(snapshots):\n"
        #template += "        return ''\n"
        template += "    try:\n"        
        template += "        with snapshot_lock:\n"
        template += "            pickled_snapshot = dill.dumps(snapshots[index])\n"
        template += "        compressed_snapshot = zlib.compress(pickled_snapshot)\n"
        template += "        hex_snapshot = compressed_snapshot.hex()\n"
        #template += "        print('request snapshot', index, len(pickled_snapshot), len(compressed_snapshot), len(hex_snapshot))\n"
        template += "        return hex_snapshot\n"
        template += "    except Exception as e:\n"
        template += "         import boltons.iterutils\n"
        template += "         non_picklable = boltons.iterutils.research(snapshots[index], query=lambda p, k, v: type(v) not in [list, dict, set, tuple] and not dill.pickles(v))\n"
        template += "         if non_picklable:\n"
        template += "             print('not picklable:', non_picklable)\n"
        template += "         raise\n"


        template += "@app.route('/command', methods=['POST'])\n"
        template += "def endpoint_event():\n"
        template += "    from flask import request\n"
        template += "    global status\n"
        template += "    data = request.json\n"
        template += "    if data['type'] == 'on_pause':\n"
        template += "        graph.active_training_node.layer.on_pause()\n"
        template += "    elif data['type'] == 'on_resume':\n"
        template += "        graph.active_training_node.layer.on_resume()\n"
        template += "    elif data['type'] == 'on_start':\n"
        template += "        status = STATUS_STARTED\n"
        template += "    elif data['type'] == 'on_stop':\n"
        template += "        status = STATUS_STOPPED\n"
        template += "    return jsonify(success=True)\n"

        template += "@app.route('/')\n"
        template += "def endpoint_index():\n"
        template += "    global status, t_start\n"
        template += "    result = {\n"
        template += "        'status': status,\n"
        template += "        'n_snapshots': len(snapshots),\n"
        template += "        'snapshot_count': len(snapshots),\n"
        template += "        'running_time': time.perf_counter() - t_start if t_start is not None else None\n"        
        template += "    }\n"
        template += "    return jsonify(result)\n"        

        template += "snapshot_builder = SnapshotBuilder(\n"
        template += "    BASE_TO_REPLICA_MAP, \n"
        template += "    REPLICATED_PROPERTIES_TABLE\n"
        template += ")\n"
        template += "\n"
        template += "def make_snapshot(graph):\n"
        template += "    global snapshot_lock, snapshots\n"        
        template += "    with snapshot_lock:\n"
        template += "        snapshot = snapshot_builder.build(graph)\n"
        template += "        snapshots.append(snapshot)\n"
        template += "        socket.send_multipart([b'snapshots', dill.dumps(snapshot)])\n"
        

        # --- CREATE MAIN FUNCTION ---
        template += 'def main(wait=False):\n'
        template += '    global graph, status, t_start\n'
        
        template += '    threading.Thread(target=app.run, kwargs={"port": 5678, "threaded": True}, daemon=True).start()\n'
        template += '    graph_builder = GraphBuilder()\n'
        template += '    graph = graph_builder.build(LAYERS, EDGES)\n'
        template += '    \n'
        template += '    print(graph.training_nodes)\n'
        #template += '    graph.training_nodes[0].layer_instance.send_state_updates = synchronize_replicas\n'
        template += '    graph.training_nodes[0].layer_instance.save_snapshot = make_snapshot\n'
        
        template += '    status = STATUS_READY\n'
        template += '    if wait:\n'
        template += '        while status != STATUS_STARTED:\n'
        template += '            time.sleep(1.0)\n'
        template += '        \n'
        template += '        status = STATUS_RUNNING\n'
        template += '        t_start = time.perf_counter()\n'
        template += '        graph.training_nodes[0].layer_instance.run(graph)\n'
        template += '        \n'
        template += '        if status != STATUS_STOPPED:\n'
        template += '            status = STATUS_IDLE\n'
        template += '        while status != STATUS_STOPPED:\n'
        template += '            time.sleep(1.0)\n'        
        template += '    else:\n'
        template += '        status = STATUS_RUNNING\n'
        template += '        t_start = time.perf_counter()\n'        
        template += '        graph.training_nodues[0].layer_instance.run(graph)\n'
        template += '\n'        
        template += '    status = STATUS_DONE\n'        
        template += '\n\n'
        template += 'if __name__ == "__main__":\n'
        template += '    wait = "--wait" in sys.argv\n'
        template += '    main()\n'
        
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


        ast.parse(code)
            
        
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
    
        
        
        
        
    

    
