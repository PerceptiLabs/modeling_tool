import logging
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.trainer.model import TrainingModel
from perceptilabs.graph.spec import GraphSpec

logger = logging.getLogger(APPLICATION_LOGGER)


class ModelAccess:
    def __init__(self, script_factory):    
        self._script_factory = script_factory

    def get_training_model(self, model_id, checkpoint_path=None):
        training_model = TrainingModel(
            self._script_factory, self.get_graph_spec(model_id))

        if checkpoint_path:
            training_model.load_weights(filepath=checkpoint_path)
            logger.info(f"Loaded weights from {checkpoint_path}")
            
        return training_model

    def get_graph_spec(self, model_id):
        graph_spec = GraphSpec.from_dict(model_id)  # TODO: this should be retrieved from rygg
        return graph_spec

