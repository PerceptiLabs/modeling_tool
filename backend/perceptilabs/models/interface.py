import os
import logging

from perceptilabs.stats.base import OutputStats
from perceptilabs.exporter.base import Exporter, CompatibilityError
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.data.base import DataLoader
from perceptilabs.resources.files import FileAccess


logger = logging.getLogger(APPLICATION_LOGGER)


class ModelsInterface:
    def __init__(self, task_executor, message_broker, model_access, epochs_access, training_results_access, testing_results_access, data_metadata_cache):
        self._task_executor = task_executor
        self._message_broker = message_broker
        self._model_access = model_access        
        self._epochs_access = epochs_access
        self._training_results_access = training_results_access
        self._testing_results_access = testing_results_access        
        self._data_metadata_cache = data_metadata_cache

    def start_training(self, dataset_settings_dict, model_id, graph_spec_dict, training_session_id, training_settings, load_checkpoint, user_email):
        self._task_executor.enqueue('training_task', dataset_settings_dict, model_id, graph_spec_dict, training_session_id, training_settings, load_checkpoint, user_email)

    def stop_training(self, model_id, training_session_id):
        self._message_broker.publish(
            {'event': 'training-stop', 'payload': {'model_id': model_id, 'training_session_id': training_session_id}})        

    def pause_training(self, model_id, training_session_id):
        self._message_broker.publish(
            {'event': 'training-pause', 'payload': {'model_id': model_id, 'training_session_id': training_session_id}})

    def unpause_training(self, model_id, training_session_id):
        self._message_broker.publish(
            {'event': 'training-unpause', 'payload': {'model_id': model_id, 'training_session_id': training_session_id}})
        
    def get_training_status(self, model_id, training_session_id):
        results_dict = self._training_results_access.get_latest(training_session_id)

        if results_dict:
            result = {
                "Status": results_dict.get("trainingStatus"),
                "Iterations": results_dict.get("iter"),
                "Epoch": results_dict.get("epoch"),
                "Progress": results_dict.get("progress"),
                "CPU": results_dict.get("cpu_usage"),
                "GPU": results_dict.get("gpu_usage"),
                "Memory": results_dict.get("mem_usage"),
                "Training_Duration": results_dict.get("training_duration"),
                "error": results_dict.get("error"),                
            }
            return result
        else:
            return {}

    def get_training_results(self, model_id, training_session_id, type_, layer_id=None, view=None):
        results_dict = self._training_results_access.get_latest(training_session_id)

        if not results_dict:
            return {}

        if type_ == 'global-results':
            stats = results_dict['global_stats']
            output = stats.get_data_objects()
            return output
        elif type_ == 'end-results':
            global_stats = results_dict['global_stats']
        
            output = {}        
            output['global_stats'] = global_stats.get_end_results()
        
            for layer_id, obj in results_dict['layer_stats'].items():
                if isinstance(obj, OutputStats):  # OutputStats are guaranteed to have end results
                    output[layer_id] = obj.get_end_results()

            return output
        elif type_ == 'layer-results':
            stats = results_dict['layer_stats'][layer_id]        
            output = stats.get_data_objects(view=view)            
            return output

    def has_checkpoint(self, model_id, training_session_id):
        return self._epochs_access.has_saved_epoch(
            training_session_id, require_trainer_state=False)
        
    def export(self, options, model_id, graph_spec_dict, dataset_settings_dict, training_session_id, user_email):
        if self.has_checkpoint(model_id, training_session_id):
            return self._export_after_training(options, model_id, graph_spec_dict, dataset_settings_dict, training_session_id, user_email)
        else:
            return self._export_while_training(options, model_id, training_session_id)            

    def _export_while_training(self, options, model_id, training_session_id):
        export_path = os.path.join(options['Location'], options['name'])
        mode = self._get_export_mode(options)
        
        message = {
            'event': 'training-export',
            'payload': {
                'model_id': model_id,
                'training_session_id': training_session_id,                
                'export_directory': export_path,
                'mode': mode
            }
        }
        self._message_broker.publish(message)        
        return f"Model is running: export requested to {export_path}. This may take a moment."
        
    def _export_after_training(self, options, model_id, graph_spec_dict, dataset_settings_dict, training_session_id, user_email):        
        try:
            graph_spec = self._model_access.get_graph_spec(
                model_id=graph_spec_dict) #TODO: F/E should send an ID
            
            data_loader = self._get_data_loader(dataset_settings_dict, user_email)

            epoch_id = self._epochs_access.get_latest(
                training_session_id=training_session_id,  
                require_checkpoint=True,
                require_trainer_state=False
            )

            checkpoint_path = self._epochs_access.get_checkpoint_path(
                training_session_id=training_session_id,
                epoch_id=epoch_id
            )
            training_model = self._model_access.get_training_model(
                graph_spec.to_dict(),  # TODO. f/e should send an ID
                checkpoint_path=checkpoint_path
            )
            
            exporter = Exporter(
                graph_spec, training_model, data_loader, model_id=model_id, user_email=user_email)
            
            export_path = os.path.join(options['Location'], options['name'])
            mode = self._get_export_mode(options)
            exporter.export(export_path, mode=mode)

        except CompatibilityError:
            return "Model not compatible."
        except Exception as e:
            logging.exception("Model export failed")
            return f"Model export failed"
        else:
            return f"Model exported to '{export_path}'"

    def _get_export_mode(self, export_settings):
        type_ = export_settings['Type']
        if type_== 'TFModel':
            if export_settings['Compressed']:
                mode = 'Compressed'
            elif export_settings['Quantized']:
                mode = 'Quantized'
            else:
                mode = 'Standard'
        else:
            mode = type_
        return mode

    def _get_data_loader(self, settings_dict, user_email):
        dataset_settings = DatasetSettings.from_dict(settings_dict)
        csv_path = settings_dict['filePath']  # TODO: move one level up
        
        key = ['pipelines', user_email, csv_path, dataset_settings.compute_hash()]

        cache = self._data_metadata_cache.for_compound_keys()
        data_metadata = cache.get(key)
        
        file_access = FileAccess(os.path.dirname(csv_path))          
        data_loader = DataLoader.from_csv(
            file_access, csv_path, dataset_settings, metadata=data_metadata)

        return data_loader

    def start_testing(self, models_info, tests, user_email):
        testing_session_id = self._testing_results_access.new_id()
        self._task_executor.enqueue('testing_task', testing_session_id, models_info, tests, user_email)
        return testing_session_id
    
    def get_testing_status(self, testing_session_id):
        results_dict = self._testing_results_access.get_latest(testing_session_id)

        if results_dict:
            results = results_dict.get('status', {})
            results['error'] = results_dict.get('error')
            return results
        else:
            return {}

    def get_testing_results(self, testing_session_id):
        results_dict = self._testing_results_access.get_latest(testing_session_id)

        if results_dict:
            return results_dict['results']
        else:
            return {}
        
