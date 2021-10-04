import threading
import logging
import time
import os

import tensorflow as tf
import numpy as np
import gradio as gr


from perceptilabs.resources.epochs import EpochsAccess
from perceptilabs.resources.models import ModelAccess
from perceptilabs.resources.files import FileAccess
from perceptilabs.script import ScriptFactory
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.session.utils import Session
from perceptilabs.caching.utils import get_data_metadata_cache
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


def is_file_type(obj):
    from tempfile import _TemporaryFileWrapper
    return isinstance(obj, _TemporaryFileWrapper)


class GradioLauncher:
    def __init__(self, model_access, epochs_access):
        self._thread = None
        self._stop_event = threading.Event()

        self._model_access = model_access
        self._epochs_access = epochs_access

        self._url_dict = dict()  # multiprocessing.Manager().dict()  # So we can pass url between processes
        self._url_dict['url'] = None

    def get_url(self):
        return self._url_dict['url']

    def start(self, graph_spec, data_loader, checkpoint_directory, model_name):
        #if utils.is_debug():
        #    raise NotImplementedError("Cannot run Gradio in debug mode!")  # Flask development servers interfere
        self._thread = threading.Thread(
            target=self._worker,
            args=(graph_spec, data_loader, checkpoint_directory, model_name, self._url_dict),
            daemon=True
        )
        self._thread.start()

    def stop(self):
        # Gradio has a bug that prevents killing the server (which runs in a non-daemon thread, so killing our worker thread isn't an option).
        # Running it as a forked subprocess - which can be killed - doesn't work on Windows
        # Running it as a spawned subprocess - which can be killed - doesn't work because DataLoader etc cannot be pickled.
        
        raise NotImplementedError
        
        self._stop_event.set()
        self._thread.join()
        
    def _worker(self, graph_spec, data_loader, checkpoint_directory, model_name, url_dict):
        try:
            return self._worker_internal(
                graph_spec, data_loader, checkpoint_directory, model_name, url_dict)
        except:
            logger.exception("Error in worker")
            raise
        
    def _worker_internal(self, graph_spec, data_loader, checkpoint_directory, model_name, url_dict):        
        inference_model = self._get_inference_model(
            graph_spec, data_loader, checkpoint_directory)

        metadata = data_loader.metadata
        inputs = {
            spec.feature_name: self.get_gradio_input(spec.feature_name, spec.datatype, metadata[spec.feature_name])
            for spec in graph_spec.input_layers
        }
        targets = {
            spec.feature_name: self.get_gradio_output(spec.feature_name, spec.datatype, metadata[spec.feature_name])
            for spec in graph_spec.target_layers
        }
        
        def fn_inference(*input_values):
            x = {}

            for feature_name, value in zip(inputs.keys(), input_values):
                if is_file_type(value):
                    loader = data_loader.get_loader_pipeline(feature_name)                    
                    value = loader(value.name)

                x[feature_name] = np.array([value])
            
            y = inference_model.predict(x)

            if len(targets) == 1:
                output_values = next(iter(y.values())).squeeze().tolist()
            else:
                output_values = [y[name].squeeze().tolist() for name in targets.keys()]
            return output_values        

        interface = gr.Interface(
            title=model_name,
            article='This model was built using [PerceptiLabs](https://www.perceptilabs.com/)<br><p align="center">![image](https://assets-global.website-files.com/60adcbb2ee6df32cbf46b7cc/60aed0284f5d624b91f4ed4e_logo-footer.svg)</p>',
            thumbnail='https://assets-global.website-files.com/60adcbb2ee6df32cbf46b7cc/60aed0284f5d624b91f4ed4e_logo-footer.svg',
            fn=fn_inference,
            inputs=list(inputs.values()),
            outputs=list(targets.values())
        )
        
        flask_app, path_to_local_server, share_url = \
            interface.launch(share=False, prevent_thread_lock=True)  # Warning: Gradio conflicts with our Flask development server. URL is only valid when we run the kernel with debug == False

        url_dict['url'] = path_to_local_server

        while not self._stop_event.is_set():
            time.sleep(0.5)

        interface.close()
        
    def _get_inference_model(self, graph_spec, data_loader, checkpoint_directory):
        epoch_id = self._epochs_access.get_latest(
            training_session_id=checkpoint_directory,  # TODO: F/E should send ID
            require_checkpoint=True,
            require_trainer_state=False
        )

        checkpoint_path = self._epochs_access.get_checkpoint_path(
            training_session_id=checkpoint_directory, epoch_id=epoch_id)  # TODO: F/E should send ID

        model = self._model_access \
            .get_training_model(
                model_id=graph_spec.to_dict(),  # TODO: frontend should send a model ID
                checkpoint_path=checkpoint_path
            ).as_inference_model(data_loader, include_preprocessing=True)

        return model
        
    @staticmethod
    def get_gradio_input(feature_name, datatype, metadata):
        if datatype == 'numerical':  
            return gr.inputs.Number(default=1, label=feature_name)
        if datatype == 'categorical':  
            return gr.inputs.Radio(
                choices=list(metadata['preprocessing']['mapping'].keys()), label=feature_name)        
        elif datatype == 'text':  
            return gr.inputs.Textbox(label=feature_name)
        elif datatype == 'image':
            n_channels = metadata['loader']['n_channels']
            if n_channels == 3:
                image_mode = 'RGB'
            elif n_channels == 1:
                image_mode = 'L'  # grayscale
            else:
                raise ValueError(f"Unexpected number of channels in metadata: {n_channels}")
            
            return gr.inputs.Image(image_mode=image_mode, label=feature_name, type='file') 
        else:
            raise NotImplementedError(f"No gradio input type found for datatype '{datatype}'")

    @staticmethod
    def get_gradio_output(feature_name, datatype, metadata):
        if datatype == 'numerical':
            return gr.outputs.Textbox(label=feature_name)
        elif datatype == 'text':  
            return gr.outputs.Textbox(label=feature_name)
        elif datatype == 'image': 
            return gr.outputs.Image(type='numpy', label=feature_name)             
        elif datatype == 'categorical':
            return gr.outputs.Textbox(label=feature_name)  
        else:
            raise NotImplementedError(f"No gradio output type found for datatype '{datatype}'")

    
class GradioSession(Session):
    def __init__(self):
        self._model_access = ModelAccess(ScriptFactory())
        
        self._launcher = GradioLauncher(
            self._model_access,
            EpochsAccess()
        )
    
    def on_request_received(self, request):
        if request['action'] == 'Stop':  
            self._launcher.stop()
            return {}
        elif request['action'] == 'get_url':
            return self._launcher.get_url()

    def on_start_called(self, payload, is_retry):
        graph_spec = self._model_access.get_graph_spec(payload['network'])  # TODO: F/E should send ID
        checkpoint_directory = payload['checkpointDirectory']
        user_email = payload['userEmail']
        model_name = payload['modelName']
        

        dataset_settings = DatasetSettings.from_dict(payload['datasetSettings'])

        csv_path = payload['datasetSettings']['filePath']  # TODO: move one level up        
        data_loader = self._get_data_loader(csv_path, dataset_settings, user_email)
        self._launcher.start(graph_spec, data_loader, checkpoint_directory, model_name)

    def _get_data_loader(self, csv_path, dataset_settings, user_email):
        key = ['pipelines', user_email, dataset_settings.compute_hash()]
        cache = get_data_metadata_cache().for_compound_keys()        
        data_metadata = cache.get(key)

        file_access = FileAccess(os.path.dirname(csv_path))         
        data_loader = DataLoader.from_csv(file_access, csv_path, dataset_settings, metadata=data_metadata)        
        return data_loader
