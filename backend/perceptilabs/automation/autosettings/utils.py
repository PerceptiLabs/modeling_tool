import logging
import copy

import perceptilabs.utils as utils
from perceptilabs.automation.autosettings import DEFAULT_RULES, SettingsEngine
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.layers.specbase import DummySpec
from perceptilabs.layers import get_layer_builder
from perceptilabs.lwcore import LightweightCore
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


def setup_engine(lw_core):
    settings_engine = SettingsEngine(DEFAULT_RULES, lw_core=lw_core)
    return settings_engine


def get_recommendation(json_network, settings_engine):
    graph_spec = GraphSpec.from_dict(json_network)

    new_layer_specs = settings_engine.run(graph_spec)
    
    new_json_network = {}
    for layer_id, layer_spec in new_layer_specs.items():
        new_json_network[layer_id] = layer_spec.to_dict()
        
    return new_json_network


if __name__ == "__main__":

    engine = setup_engine(None)

    import json
    with open('net.json_', 'r') as f:
        json_network = json.load(f)['Layers']
        
    rec = get_recommendation(json_network, engine)
    #rec = get_recommendation(json_network, ['1588690292610'], engine)    

    import pprint



    print("original")
    pprint.pprint(json_network)
    print("recommended")    
    pprint.pprint(rec)
    
    import pdb; pdb.set_trace()
    
