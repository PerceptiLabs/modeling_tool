import threading
import logging
import time

import numpy as np
import gradio as gr

from perceptilabs.resources.epochs import EpochsAccess
from perceptilabs.resources.models import ModelAccess
from perceptilabs.resources.serving_results import ServingResultsAccess
from perceptilabs.script import ScriptFactory
from perceptilabs.trainer.model import TrainingModel
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.caching.utils import get_data_metadata_cache


logger = logging.getLogger(__name__)


def is_file_type(obj):
    from tempfile import _TemporaryFileWrapper
    return isinstance(obj, _TemporaryFileWrapper)


class GradioStrategy:
    def __init__(self, call_context, model_access, epochs_access, model_id, graph_spec, data_loader, training_session_id, model_name, on_serving_started=None, include_preprocessing=True, include_postprocessing=True):
        self._thread = None
        self._call_context = call_context
        self._stop_event = threading.Event()

        self._model_access = model_access
        self._epochs_access = epochs_access

        self._url_dict = dict()  # multiprocessing.Manager().dict()  # So we can pass url between processes
        self._url_dict['url'] = None
        self._running = False

        self._model_id = model_id
        self._graph_spec = graph_spec
        self._data_loader = data_loader
        self._training_session_id = training_session_id
        self._model_name = model_name
        self._on_serving_started = on_serving_started
        self._include_preprocessing = include_preprocessing
        self._include_postprocessing = include_postprocessing
        
    def get_url(self):
        return self._url_dict['url']

    def get_path(self):
        return None

    @property
    def is_running(self):
        return self._running

    def cleanup(self):
        pass

    def start(self):
        self._running = True
        self._thread = threading.Thread(
            target=self._worker,
            args=(
                self._call_context,
                self._model_id,
                self._graph_spec,
                self._data_loader,
                self._training_session_id,
                self._model_name,
                self._url_dict,
                self._on_serving_started,
                self._include_preprocessing,
                self._include_postprocessing
            ),
            daemon=True
        )
        self._thread.start()

    def stop(self):
        self._running = False
        self._stop_worker()
        
    def _stop_worker(self):
        # Gradio has a bug that prevents killing the server (which runs in a non-daemon thread, so killing our worker thread isn't an option).
        # Running it as a forked subprocess - which can be killed - doesn't work on Windows
        # Running it as a spawned subprocess - which can be killed - doesn't work because DataLoader etc cannot be pickled.
        raise NotImplementedError()        
        # self._stop_event.set()
        # self._thread.join()

    def _worker(self, call_context, model_id, graph_spec, data_loader, training_session_id, model_name, url_dict, on_serving_started, include_preprocessing=True, include_postprocessing=True):
        try:
            return self._worker_internal(
                call_context,
                model_id,
                graph_spec,
                data_loader,
                training_session_id,
                model_name,
                url_dict,
                on_serving_started,
                include_preprocessing=include_preprocessing,
                include_postprocessing=include_postprocessing)
        except:
            logger.exception("Error in worker")
            raise

    def _worker_internal(self, call_context, model_id, graph_spec, data_loader, training_session_id, model_name, url_dict, on_serving_started, include_preprocessing=True, include_postprocessing=True):
        inference_model = self._get_inference_model(
            call_context,
            model_id,
            graph_spec,
            data_loader,
            training_session_id,
            include_preprocessing=include_preprocessing,
            include_postprocessing=include_postprocessing
        )
        metadata = data_loader.metadata

        inputs = {
            spec.feature_name: self.get_gradio_input(spec.feature_name, spec.datatype, metadata[spec.feature_name])
            for spec in graph_spec.input_layers
        }
        targets = {
            spec.feature_name: self.get_gradio_output(spec.feature_name, spec.datatype, metadata[spec.feature_name], include_preprocessing=include_preprocessing, include_postprocessing=include_postprocessing)
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
            output_values = self._create_output_values(y, targets, metadata, graph_spec, include_preprocessing=include_preprocessing, include_postprocessing=include_postprocessing)

            return output_values

        examples = self._get_gradio_examples(data_loader=data_loader, include_preprocessing=include_preprocessing, include_postprocessing=include_postprocessing)
        interface = gr.Interface(
            title=model_name,
            article='This model was built using [PerceptiLabs](https://www.perceptilabs.com/)<br><p align="center">![image](https://assets-global.website-files.com/60adcbb2ee6df32cbf46b7cc/60aed0284f5d624b91f4ed4e_logo-footer.svg)</p>',
            thumbnail='https://assets-global.website-files.com/60adcbb2ee6df32cbf46b7cc/60aed0284f5d624b91f4ed4e_logo-footer.svg',
            fn=fn_inference,
            inputs=list(inputs.values()),
            outputs=list(targets.values()),
            examples=examples
        )

        flask_app, path_to_local_server, share_url = \
            interface.launch(share=False, prevent_thread_lock=True)  # Warning: Gradio conflicts with our Flask development server. URL is only valid when we run the kernel with debug == False


        url_dict['url'] = path_to_local_server

        if on_serving_started:
            on_serving_started()

        while not self._stop_event.is_set():
            time.sleep(0.5)

        interface.close()
        ServingResultsAccess.remove_gradio_examples_dir()

    def _get_inference_model(self, call_context, model_id, graph_spec, data_loader, training_session_id, include_preprocessing=True, include_postprocessing=True):
        epoch_id = self._epochs_access.get_latest(
            call_context,
            training_session_id=training_session_id,
            require_checkpoint=True,
            require_trainer_state=False
        )

        checkpoint_path = self._epochs_access.get_checkpoint_path(
            call_context,
            training_session_id=training_session_id, epoch_id=epoch_id)

        training_model = TrainingModel.from_graph_spec(
            graph_spec, checkpoint_path=checkpoint_path)

        inference_model = training_model.as_inference_model(
            data_loader, include_preprocessing=include_preprocessing, include_postprocessing=include_postprocessing)

        return inference_model

    def _create_output_values(self, model_output, targets, metadata, graph_spec, include_preprocessing=True, include_postprocessing=True):
        if len(targets) == 1:
            output_values = next(iter(model_output.values())).squeeze().tolist()
        else:
            output_values = [model_output[name].squeeze().tolist() for name in targets.keys()]

        dtype = self._get_dtype(graph_spec.target_layers)
        if not include_postprocessing and dtype=='categorical':
            output_values = self._create_categorical_output(model_output, metadata, graph_spec)

        return output_values

    def _create_categorical_output(self, model_output, metadata, graph_spec):
        categories = self._get_all_categories(metadata=metadata, target_layers=graph_spec.target_layers)
        output_values = dict()
        for value in model_output.values():
            if isinstance(value, np.ndarray) and value.ndim > 1:
                predictions = value.flatten().tolist()
            for index in range(len(categories)):
                output_values[categories[index]] = predictions[index]
        return output_values

    def _get_all_categories(self, metadata, target_layers):
        if len(target_layers) > 1:
            raise NotImplementedError("Can't get categories when there is more than one target layer!")
        for spec in target_layers:
            categories = list(metadata[spec.feature_name]['preprocessing']['mapping'].keys())
            return categories
    
    def _get_gradio_examples(self, data_loader, include_preprocessing, include_postprocessing):
        if not include_preprocessing or not include_postprocessing:
            return
        
        # Get the first column since that's the input
        test_set_df = data_loader.get_data_frame(partition='test')

        if len(test_set_df) > 0:
            samples = test_set_df.sample(n=3).values.tolist()
            examples = ServingResultsAccess.create_dir_for_gradio_examples(samples=samples) # A list of paths
            return examples

    def _get_dtype(self, target_layers):
        for spec in target_layers:
            dtype = spec.datatype
            return dtype

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
    def get_gradio_output(feature_name, datatype, metadata, include_preprocessing=True, include_postprocessing=True):
        if datatype == 'numerical':
            return gr.outputs.Textbox(label=feature_name)
        elif datatype == 'text':
            return gr.outputs.Textbox(label=feature_name)
        elif datatype in ['image', 'mask']:
            return gr.outputs.Image(type='numpy', label=feature_name)
        elif datatype == 'categorical':
            if include_postprocessing:
                return gr.outputs.Textbox(label=feature_name)
            else:
                return gr.outputs.Label(type='confidences', label=feature_name)
        else:
            raise NotImplementedError(f"No gradio output type found for datatype '{datatype}'")

