# Generated by Django 3.2 on 2021-11-29 18:29

from django.db import migrations



# Generated by Django 3.2 on 2021-11-24 19:42

from django.db import migrations
from rygg.api.models import Model
import json
import logging
import os

logger = logging.getLogger(__name__)
# rygg.settings isn't obeyed. Make it obey
logger.setLevel(os.getenv('PL_RYGG_LOG_LEVEL', 'WARNING'))


def path_join(*paths):
    return os.path.join(*paths).replace('\\','/')

def fix_path(path):
    return os.path.expanduser(path).replace('\\','/')

def files_to_fix():
    # call objects() instead of available_objects() to migrate all models, just in case...
    for result in Model.objects.values('location'):
        raw_location = result.get('location')
        if not raw_location:
            continue

        logging.debug(f"Found model with location {raw_location}")
        abs_location = fix_path(raw_location)
        if not os.path.isdir(abs_location):
            logging.debug(f"Location {raw_location} doesn't exist on disk. Skipping.")
            continue

        yield path_join(abs_location, "model.json")

def make_graph_settings(elements):
    layers = {}
    for id_, el in elements.items():
        layers[id_] = {
            'Name': el['layerName'],
            'Type': el['componentName'],
            'Properties': el['layerSettings'],
            'Code': el['layerCode'],
            'backward_connections': el['backward_connections'],
            'forward_connections': el['forward_connections'],
            'visited': el['visited'],
            'previewVariable': el['previewVariable']
        }
    return layers

def make_layer_meta(elements):
    """ 
    Drop everything used in the Kernel. 
    The frontend still uses these, but this way there's a single source of truth
    """
    for el in elements.values():
        del el['layerName']
        del el['componentName'],
        del el['layerSettings'],
        del el['layerCode'],
        del el['backward_connections'],
        del el['forward_connections'],
        del el['visited'],
        del el['previewVariable']
    
    return elements

def make_network_element_list(graph_settings, layer_meta):
    elements = {}

    for id_ in layer_meta.keys():
        el = layer_meta[id_]

        el['layerName'] = graph_settings[id_]['Name']
        el['componentName'] = graph_settings[id_]['Type']
        el['layerSettings'] = graph_settings[id_]['Properties']
        el['layerCode'] = graph_settings[id_]['Code']
        el['backward_connections'] = graph_settings[id_]['backward_connections']
        el['forward_connections'] = graph_settings[id_]['forward_connections']
        el['visited'] = graph_settings[id_]['visited']
        el['previewVariable'] = graph_settings[id_]['previewVariable']

        elements[id_] = el        

    return elements

def apply_migration(path):
    try:
        with open(path, 'r') as f:
            dict_in = json.load(f)

        graph_settings = make_graph_settings(dict_in['networkElementList'])
        
        frontend_settings = {
            'apiMeta': dict_in['apiMeta'],
            'networkName': dict_in['networkName'],            
            'networkRootFolder': dict_in['networkRootFolder'],
            'networkMeta': dict_in['networkMeta'],
            'layerMeta': make_layer_meta(dict_in['networkElementList'])
        }

        dict_out = {
            'datasetSettings': dict_in['datasetSettings'],
            'trainingSettings': dict_in['trainingSettings'],
            'frontendSettings': frontend_settings,
            'graphSettings': graph_settings
        }
        
        with open(path, 'w') as f:
            json.dump(dict_out, f)            
    except:
        logger.debug(f"Exception when trying to undo migration of {path}.. Skipping.")
    else:
        logger.debug(f"Successfully applied migration of {path}")    

def undo_migration(path):
    try:
        with open(path, 'r') as f:
            dict_in = json.load(f)

        dict_out = {
            'apiMeta': dict_in['frontendSettings']['apiMeta'],
            'networkName': dict_in['frontendSettings']['networkName'],
            'networkRootFolder': dict_in['frontendSettings']['networkRootFolder'],
            'networkMeta': dict_in['frontendSettings']['networkMeta'],
            'datasetSettings': dict_in['datasetSettings'],
            'trainingSettings': dict_in['trainingSettings'],               
            'networkElementList': make_network_element_list(
                dict_in['graphSettings'], dict_in['frontendSettings']['layerMeta'])
        }
        
        with open(path, 'w') as f:
            json.dump(dict_out, f)            
    except:
        logger.debug(f"Exception when trying to undo migration of {path}.. Skipping.")        
    else:
        logger.debug(f"Successfully undid migration of {path}")    
        
def fn_forwards(app, schema_editor):
    for path in files_to_fix():
        apply_migration(path)

def fn_reverse(app, schema_editor):
    for path in files_to_fix():
        undo_migration(path)
        
class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_training_and_dataset_settings_to_root'),
    ]

    operations = [
        migrations.RunPython(fn_forwards, fn_reverse)        
    ]
