import os
import logging
from perceptilabs.trainer.model import TrainingModel
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.script import ScriptFactory


logger = logging.getLogger(__name__)


class ModelAccess:
    def __init__(self, rygg):
        self._rygg = rygg

    def get_graph_spec(self, call_context, model_id, default_settings=None):
        graph_settings = self.get_graph(call_context, model_id)

        if graph_settings is None:
            graph_settings = default_settings

        graph_spec = GraphSpec.from_dict(graph_settings)
        return graph_spec

    def create(self, call_context, dataset_id, model_name, model_path=None):
        location = os.path.join(model_path, model_name) if model_path else None
        res = self._rygg.create_model(
            call_context, dataset_id, model_name, location=location
        )
        return res["model_id"]

    def save_graph(self, call_context, model_id, graph_spec):
        model = self._rygg.load_model_json(call_context, model_id)
        model["graphSettings"] = graph_spec.to_dict()
        self._rygg.save_model_json(call_context, model_id, model)

    def get_graph(self, call_context, model_id):
        try:
            model = self._rygg.load_model_json(call_context, model_id)
            return model["graphSettings"]
        except:
            logger.exception(f"Failed getting graphSettings for model {model_id}")
            return None

    def get_training_model(
        self, call_context, model_id, default_graph_settings=None, checkpoint_path=None
    ):
        graph_spec = self.get_graph_spec(
            call_context, model_id, default_settings=default_graph_settings
        )

        training_model = TrainingModel.from_graph_spec(
            graph_spec, checkpoint_path=checkpoint_path
        )

        return training_model
