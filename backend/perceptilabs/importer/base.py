import pandas as pd
import json
import logging
from perceptilabs.data.type_inference import TypeInferrer
from perceptilabs.graph.spec import GraphSpec


logger = logging.getLogger(__name__)
        
class Importer:
    def __init__(self, dataset_access):
        self._dataset_access = dataset_access
    
    def run(self, dataset_id, file_location):
        with open(file_location, 'r') as f:
            content = json.load(f)

        dataset_settings_dict = content['networkMeta']['datasetSettings']
        dataset_location = self._dataset_access.get_location(dataset_id)


        original_dataset_id = dataset_settings_dict['datasetId']
        
        if dataset_id != original_dataset_id:
            dataset_settings_dict['datasetId'] = dataset_id
            dataset_settings_dict['filePath'] = dataset_location

        new_dataset = self._dataset_access.get_name(dataset_id)                
        original_dataset = self._dataset_access.get_name(dataset_id)
        
        type_inferrer = TypeInferrer.with_default_settings()        
        df = pd.read_csv(dataset_location)
        
        default_types = {
            name: type_inferrer.get_default_datatype(series)
            for name, series in df.items()
        }

        # TODO(anton): loop over type inference to see what works...!        

        mapping = {original_column: None for original_column in dataset_settings_dict['featureSpecs'].keys()}

        expected_types = set()
        for new_column, actual_type in default_types.items():
            for original_column, spec in dataset_settings_dict['featureSpecs'].items():
                expected_type = spec['datatype']
                expected_types.add(expected_type)
                
                if actual_type == expected_type:
                    mapping[original_column] = new_column

        for original_column, new_column in mapping.items():
            if new_column is None:
                message  = f"Couldn't find a suitable remapping of dataset columns. The recommended types for dataset '{new_dataset}' were "
                message += ", ".join(k + '->' + v for k, v in default_types.items())
                message += ", but the model expects the types " + ", ".join(expected_types)
                raise ValueError(message)

            if new_column != original_column:            
                dataset_settings_dict['featureSpecs'][new_column] = dataset_settings_dict['featureSpecs'][original_column]
                del dataset_settings_dict['featureSpecs'][original_column]
                logger.info(
                    f"Remapped '{original_column}' (dataset: {original_dataset_id}) -> '{new_column}' (dataset (dataset: {dataset_id})")
            else:
                logger.info(
                    f"Column '{new_column}' present in both datasets. No remapping needed")

                
        training_settings_dict = content['networkMeta']['trainingSettings']


        # TODO: refactor... we should rely on the graph spec for ground truth...
        layers = {}
        for layer_id, el in content['networkElementList'].items():
            layers[layer_id] = {
                'Name': el['layerName'],  # TODO: layer names are the old ones
                'Type': el['componentName'],
                'endPoints': el['endPoints'],
                'Properties': el['layerSettings'],
                'Code': el['layerCode'],
                'backward_connections': el['backward_connections'],
                'forward_connections': el['forward_connections'],
                'visited': el['visited'],
                'previewVariable': el['previewVariable']
            }

            if 'FeatureName' in layers[layer_id]['Properties']:
                original_column = layers[layer_id]['Properties']['FeatureName']  # TODO: make prettier?
                layers[layer_id]['Properties']['FeatureName'] = mapping[original_column]


        graph_spec = GraphSpec.from_dict(layers)
        graph_spec_dict = graph_spec.to_dict()  # Just for validation...

        #graph_spec.show()

        return dataset_settings_dict, graph_spec_dict, training_settings_dict
    


    
