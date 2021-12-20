import os
import json
import logging
from zipfile import ZipFile


logger = logging.getLogger(__name__)

class ModelArchivesAccess:
    def read(self, location):
        location = location.replace('\\', '/')
        with ZipFile(location, 'r') as archive:
            model_json = archive.read('model.json').decode('utf-8')
            content = json.loads(model_json)

        results = (
            content['datasetSettings'],
            content['graphSettings'],            
            content['trainingSettings'],
            content['frontendSettings']
        )
        logger.info(f"Successfully read model from '{location}'")
        return results

    def write(self, model_id, location, dataset_settings, graph_spec, training_settings, frontend_settings):
        content = {
            'datasetSettings': dataset_settings,
            'graphSettings': graph_spec,            
            'trainingSettings': training_settings,
            'frontendSettings': frontend_settings
        }

        path = os.path.join(location, f'model_{model_id}.zip').replace('\\', '/')

        with ZipFile(path, 'w') as archive:
            model_json = json.dumps(content, indent=4)
            archive.writestr('model.json', model_json)

        logger.info(f"Successfully wrote model to '{path}'")
        return path

            
    
    
