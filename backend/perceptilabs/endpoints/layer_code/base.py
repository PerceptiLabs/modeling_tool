from flask import request, jsonify
from flask.views import View


from perceptilabs.graph.spec import GraphSpec
from perceptilabs.script import ScriptFactory


class LayerCode(View):
    script_factory = ScriptFactory()

    def __init__(self, model_access):
        self._model_access = model_access
    
    def dispatch_request(self):
        """ Renders the code for a layer """
        json_data = request.get_json()
        graph_spec = self._model_access.get_graph_spec(model_id=json_data['network']) #TODO: F/E should send an ID
        layer_spec = graph_spec.nodes_by_id[json_data['layer_id']]
        
        code = self.script_factory.render_layer_code(
                layer_spec,
                macro_kwargs={'layer_spec': layer_spec, 'graph_spec': graph_spec}
        )
        output = {'Output': code}        
        return jsonify(output)
