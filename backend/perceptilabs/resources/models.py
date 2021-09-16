import logging
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.trainer.model import TrainingModel

logger = logging.getLogger(APPLICATION_LOGGER)


class ModelAccess:
    def __init__(self, script_factory):    
        self._script_factory = script_factory

    def get_training_model(self, model_id, checkpoint_path=None):
        training_model = TrainingModel(
            self._script_factory, self._get_graph_spec(model_id))

        if checkpoint_path:
            training_model.load_weights(filepath=checkpoint_path)
            logger.info(f"Loaded weights from {checkpoint_path}")
            
        return training_model

    def _get_graph_spec(self, model_id):
        graph_spec = model_id  # TODO: this should be retrieved from rygg
        return graph_spec

