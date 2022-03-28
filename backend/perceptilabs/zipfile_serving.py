import os
import time
import logging

from perceptilabs.trainer.model import TrainingModel
from perceptilabs.sharing.exporter import Exporter


logger = logging.getLogger(__name__)


class ZipfileStrategy:
    def __init__(self, call_context, model_archives_access, epochs_access, model_id, graph_spec, data_loader, training_session_id, model_name, export_settings, export_directory, target_url, on_serving_started=None, include_preprocessing=True, include_postprocessing=True, ttl=None, dataset_settings=None, graph_settings=None, training_settings=None, frontend_settings=None):
        self._call_context = call_context
        self._model_archives_access = model_archives_access
        self._epochs_access = epochs_access
        self._export_settings = export_settings
        self._export_directory = export_directory
        self._model_id = model_id
        self._graph_spec = graph_spec
        self._data_loader = data_loader
        self._training_session_id = training_session_id
        self._model_name = model_name
        self._on_serving_started = on_serving_started
        self._include_preprocessing = include_preprocessing
        self._include_postprocessing = include_postprocessing
        self._dataset_settings = dataset_settings
        self._frontend_settings = frontend_settings
        self._graph_settings = graph_settings
        self._training_settings = training_settings        
        self._target_url = target_url
        self._zipfile_path = os.path.join(self._export_directory, 'model.zip').replace('\\', '/')
        self._time_started = None
        self._ttl = ttl
        
    def get_url(self):
        return self._target_url

    def get_path(self):
        if os.path.exists(self._zipfile_path):
            return self._zipfile_path
        else:
            return None

    def stop(self):
        pass

    @property
    def is_running(self):
        if self._time_started is None:
            return False
        elif self._ttl is None:
            return True
        else:
            time_running = time.perf_counter() - self._time_started
            return time_running < self._ttl
                 
    def start(self):
        if self._export_settings['Type'] == 'PlPackage':
            created_paths = {}
        else:
            created_paths = {}
            for relative_path in self._export_non_archive():
                file_path = os.path.join(
                    self._export_directory, relative_path).replace('\\', '/')
                created_paths[file_path] = relative_path

        self._model_archives_access.write(
            self._zipfile_path,
            graph_spec=self._graph_settings,
            training_settings=self._training_settings,
            frontend_settings=self._frontend_settings,
            dataset_settings=self._dataset_settings,
            extra_paths=created_paths
        )
        
        logger.info(
            f"Model archive write called for path {self._zipfile_path}")

        if self._on_serving_started:
            self._on_serving_started()                    

        self._time_started = time.perf_counter()

    def _export_archive(self):
        return []
        
    def _export_non_archive(self):        
        epoch_id = self._epochs_access.get_latest(
            self._call_context,
            training_session_id=self._training_session_id,  
            require_checkpoint=True,
            require_trainer_state=False
        )

        logger.info(
            f"Retrieved latest epoch id {epoch_id} for training session {self._training_session_id}")
            
        checkpoint_path = self._epochs_access.get_checkpoint_path(
            self._call_context,
            training_session_id=self._training_session_id,
            epoch_id=epoch_id
        )

        logger.info(
            f"Retrieved latest checkpoint path {checkpoint_path} for training session {self._training_session_id}")

        training_model = TrainingModel.from_graph_spec(
            self._graph_spec, checkpoint_path=checkpoint_path)
        
        exporter = Exporter(
            self._graph_spec, training_model, self._data_loader)

        created_files = exporter.export(
            self._export_directory,
            mode=Exporter.parse_export_mode(self._export_settings),
            include_preprocessing=self._include_preprocessing,
            include_postprocessing=self._include_postprocessing
        )
        logger.info(f"Export called for path {self._export_directory}")
        return created_files

