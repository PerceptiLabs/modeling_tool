import os
import sys
import logging

from perceptilabs.trainer.model import TrainingModel            
from perceptilabs.stats.base import OutputStats
from perceptilabs.sharing.exporter import Exporter, CompatibilityError
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.data.base import DataLoader
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.utils import KernelError
from perceptilabs.lwcore import LightweightCore
from perceptilabs.script import ScriptFactory
from perceptilabs.sharing.importer import Importer
import perceptilabs.lwcore.utils as lwcore_utils
import perceptilabs.automation.utils as automation_utils
import perceptilabs.tracking as tracking

logger = logging.getLogger(__name__)


class ModelsInterface:
    def __init__(self, task_executor, message_broker, event_tracker, dataset_access, model_access, model_archives_access, epochs_access, training_results_access, preprocessing_results_access, preview_cache, tensorflow_support_access):
        self._task_executor = task_executor
        self._message_broker = message_broker
        self._event_tracker = event_tracker
        self._dataset_access = dataset_access                
        self._model_access = model_access
        self._model_archives_access = model_archives_access                
        self._epochs_access = epochs_access
        self._training_results_access = training_results_access
        self._preprocessing_results_access = preprocessing_results_access
        self._preview_cache = preview_cache
        self._tensorflow_support_access = tensorflow_support_access
        
        self._script_factory = ScriptFactory()        
        

    def start_training(self, dataset_settings_dict, model_id, training_settings, load_checkpoint, user_email, logrocket_url='', graph_settings=None):
        training_session_id = model_id  # Training session ID == model ID for now...
        
        self._task_executor.enqueue(
            'training_task',
            dataset_settings_dict,
            model_id,
            training_session_id,
            training_settings,
            load_checkpoint,
            user_email,
            logrocket_url=logrocket_url,
            graph_settings=graph_settings
        )
        return training_session_id 
        
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
            logger.error(
                f"No results found for training session {training_session_id} and model {model_id}")
            return {}

        if type_ == 'global-results':
            return self._get_training_results_global(results_dict)
        elif type_ == 'end-results':
            return self._get_training_results_end(results_dict)
        elif type_ == 'layer-results':
            return self._get_training_results_for_layer(results_dict, layer_id, view)

    def _get_training_results_global(self, results_dict):
        stats = results_dict['global_stats']
        output = stats.get_data_objects()
        return output

    def _get_training_results_end(self, results_dict):
        global_stats = results_dict['global_stats']
        
        output = {}        
        output['global_stats'] = global_stats.get_end_results()
        
        for layer_id, obj in results_dict['layer_stats'].items():
            if isinstance(obj, OutputStats):  # OutputStats are guaranteed to have end results
                output[layer_id] = obj.get_end_results()

        return output

    def _get_training_results_for_layer(self, results_dict, layer_id, view):
        try:
            stats = results_dict['layer_stats'][layer_id]        
            output = stats.get_data_objects(view=view)
        except:
            logger.exception(
                f"Failed getting results for layer {layer_id} and view {view}. Results: {results_dict}")
            raise
        else:
            return output            

    def has_checkpoint(self, model_id, training_session_id):
        return self._epochs_access.has_saved_epoch(
            training_session_id, require_trainer_state=False)
        
    def export(self, *args, **kwargs):
        try:
            return self._export_internal(*args, **kwargs)
        except Exception as e:
            raise KernelError.from_exception(e, message=f'Model export failed')            

    def _export_internal(self, options, model_id, dataset_settings_dict, training_session_id, user_email, training_settings_dict, frontend_settings, graph_settings=None):
        if options['Type'] == 'Archive':
            return self._export_as_archive(
                model_id,
                options['Location'],
                dataset_settings_dict,
                user_email,
                training_settings_dict,
                frontend_settings,
                graph_settings=graph_settings
            )
        elif self.has_checkpoint(model_id, training_session_id):
            return self._export_after_training(
                options, model_id, dataset_settings_dict,
                training_session_id, user_email, graph_settings=graph_settings)
        else:
            return self._export_while_training(
                options, model_id, training_session_id, user_email)            

    def _export_while_training(self, options, model_id, training_session_id, graph_settings, user_email):
        export_path = os.path.join(options['Location'], options['name'])
        mode = self._get_export_mode(options)
        
        message = {
            'event': 'training-export',
            'payload': {
                'model_id': model_id,
                'training_session_id': training_session_id,                
                'export_directory': export_path,
                'graph_settings': graph_settings,
                'mode': mode,
                'user_email': user_email
            }
        }
        self._message_broker.publish(message)        
        return f"Model is running: export requested to {export_path}. This may take a moment."
        
    def _export_after_training(self, options, model_id, dataset_settings_dict, training_session_id, user_email, graph_settings):
        if graph_settings:
            graph_spec = GraphSpec.from_dict(graph_settings)
        else:
            graph_spec = self._model_access.get_graph_spec(model_id)
            
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
            
        training_model = TrainingModel.from_graph_spec(
            graph_spec, checkpoint_path=checkpoint_path)

        include_preprocessing = not options['ExcludePreProcessing'] # We not this value because the exporter has the bool parameter include_preprocessing
        include_postprocessing = not options['ExcludePostProcessing']
        exporter = Exporter(
            graph_spec, training_model, data_loader
        )
        
        export_path = os.path.join(options['Location'], options['name'])
        mode = self._get_export_mode(options)
        exporter.export(export_path, mode=mode, include_preprocessing=include_preprocessing, include_postprocessing=include_postprocessing)

        tracking.send_model_exported(
            self._event_tracker, user_email, model_id)
        
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

        data_metadata = self._preprocessing_results_access.get_metadata(
            dataset_settings.compute_hash())
        
        df = self._dataset_access.get_dataframe(
            dataset_settings.dataset_id, fix_paths_for=dataset_settings.file_based_features)

        data_loader = DataLoader(
            df,
            dataset_settings,
            metadata=data_metadata
        )
        return data_loader

    def get_layer_info(self, model_id, dataset_settings_dict, user_email, layer_id=None, graph_settings=None):
        try:
            if graph_settings:
                graph_spec = GraphSpec.from_dict(graph_settings)
            else:
                graph_spec = self._model_access.get_graph_spec(model_id)
                
            data_loader = self._get_data_loader(dataset_settings_dict, user_email)
            lw_core = self._initialize_lw_core(data_loader)
            lw_results = lw_core.run(graph_spec)

            content = lwcore_utils.get_network_data(graph_spec, lw_results, skip_previews=True)
            if layer_id is not None:
                return content[layer_id]
            else:
                return content
                    
        except Exception as e:
            raise KernelError.from_exception(e, message=f'Failed getting layer info')            

    def get_previews(self, model_id, dataset_settings_dict, user_email, graph_settings=None):
        self._tensorflow_support_access.set_tfhub_env_var()
        try:
            if graph_settings:
                graph_spec = GraphSpec.from_dict(graph_settings)
            else:
                graph_spec = self._model_access.get_graph_spec(model_id)
                
            data_loader = self._get_data_loader(dataset_settings_dict, user_email)
            lw_core = self._initialize_lw_core(data_loader)
            lw_results = lw_core.run(graph_spec)

            content = lwcore_utils.get_network_data(graph_spec, lw_results, skip_previews=False)
            preview_content, dim_content = lwcore_utils.format_content(content)

            output = {
                "previews": preview_content,  # TODO(anton.k): the best way to do this is probably to send file URLs w/ the images. That's a lot easier to debug. See: https://stackoverflow.com/questions/33279153/rest-api-file-ie-images-processing-best-practices  The problem is that the frontend expects ECharts
                "outputDims": dim_content
            }

            return output
            
        except Exception as e:
            raise KernelError.from_exception(e, message=f'Failed getting previews')            
            
    def get_layer_code(self, model_id, layer_id, graph_settings=None):
        if graph_settings:
            graph_spec = GraphSpec.from_dict(graph_settings)
        else:
            graph_spec = self._model_access.get_graph_spec(model_id)
            
        layer_spec = graph_spec.nodes_by_id[layer_id]
        code = None
        if layer_spec.is_inner_layer:  # only inner layers have code 
            code = self._script_factory.render_layer_code(
                layer_spec,
                macro_kwargs={'layer_spec': layer_spec, 'graph_spec': graph_spec}
            )
            
        output = {'Output': code}
        return output

    def get_model_recommendation(self, project_id, dataset_id, model_name, skipped_workspace, settings_dict, user_email, model_path):
        try:
            data_loader = self._get_data_loader(settings_dict, user_email)
            graph_spec, _ = automation_utils.get_model_recommendation(data_loader)

            model_id = self._model_access.create(project_id, dataset_id, model_name, model_path)
            try:
                self._model_access.save_graph(model_id, graph_spec)
            except:
                logger.warning("save_graph raised an error")
                
            
        except Exception as e:
            raise KernelError.from_exception(e, message="Couldn't get model recommendations because the Kernel responded with an error")
        
        else:
            if user_email is not None:
                self._track_model_recommended(
                    model_id, user_email, skipped_workspace, data_loader, graph_spec, settings_dict)
                
            return model_id, graph_spec.to_dict()
            
    def _track_model_recommended(self, model_id, user_email, skipped_workspace, data_loader, graph_spec, settings_dict):
        training_size = data_loader.get_dataset_size(partition='training')
        validation_size = data_loader.get_dataset_size(partition='validation')
        test_size = data_loader.get_dataset_size(partition='test')
        sample_size_bytes = sys.getsizeof(data_loader.get_sample(partition='training'))
        dataset_size_bytes = (training_size + validation_size + test_size) * sample_size_bytes
        
        is_plabs_sourced = self._dataset_access.is_perceptilabs_sourced(
            data_loader.settings.dataset_id)

        tracking.send_model_recommended(
            self._event_tracker,
            user_email,
            model_id,
            skipped_workspace,            
            settings_dict,
            dataset_size_bytes,
            graph_spec,
            is_perceptilabs_sourced=is_plabs_sourced,
            dataset_id=data_loader.settings.dataset_id
        )
    
    def import_model(self, archive_path, project_id, dataset_id, model_name, model_path):
        importer = Importer(self._dataset_access, self._model_archives_access)
        dataset_settings_dict, graph_spec_dict, training_settings_dict = \
            importer.run(dataset_id, archive_path)
        
        model_id = self._model_access.create(project_id, dataset_id, model_name, model_path)
        try:
            self._model_access.save_graph(model_id, GraphSpec.from_dict(graph_spec_dict))
        except:
            logger.warning("save_graph raised an error")

        output = {
            'modelId': model_id,
            'datasetSettings': dataset_settings_dict,
            'graphSpec': graph_spec_dict,
            'trainingSettings': training_settings_dict
        }
        
        return output

    def _export_as_archive(self, model_id, location, dataset_settings_dict, user_email, training_settings_dict, frontend_settings, graph_settings=None):
        if graph_settings is None:
            graph_settings = self._model_access.get_graph(model_id)
        
        path = self._model_archives_access.write(
            model_id,
            location,
            dataset_settings_dict,
            graph_settings,
            training_settings_dict,
            frontend_settings
        )
        tracking.send_model_exported(
            self._event_tracker, user_email, model_id)            
        return f"Model exported to '{path}'"
            

    def _initialize_lw_core(self, data_loader):
        self._tensorflow_support_access.set_tfhub_env_var()
        lw_core = LightweightCore(data_loader=data_loader, cache=self._preview_cache)
        return lw_core