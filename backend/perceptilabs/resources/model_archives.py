import os
import json
import logging
from zipfile import ZipFile


logger = logging.getLogger(__name__)


class ModelArchivesAccess:
    def read(self, location):
        location = location.replace("\\", "/")
        with ZipFile(location, "r") as archive:
            model_json = archive.read("model.json").decode("utf-8")
            content = json.loads(model_json)

        results = (
            content["datasetSettings"],
            content["graphSettings"],
            content["trainingSettings"],
            content["frontendSettings"],
        )
        logger.info(f"Successfully read model from '{location}'")
        return results

    def write(
        self,
        archive_path,
        dataset_settings=None,
        graph_spec=None,
        training_settings=None,
        frontend_settings=None,
        extra_paths=None,
    ):
        archive_path = archive_path.replace("\\", "/")
        extra_paths = extra_paths or {}

        content = {
            "datasetSettings": dataset_settings,
            "graphSettings": graph_spec,
            "trainingSettings": training_settings,
            "frontendSettings": frontend_settings,
        }

        with ZipFile(archive_path, "w") as archive:
            model_json = json.dumps(content, indent=4)
            archive.writestr("model.json", model_json)

            for included_path, arc_name in extra_paths.items():
                if arc_name is None:
                    arc_name = os.path.basename(included_path)

                archive.write(included_path, arcname=arc_name)

        logger.info(f"Successfully wrote model to '{archive_path}'")
        return archive_path
