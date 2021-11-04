import dateutil.parser

class ClientBase:
    def __init__(self, rest, id):
        self._rest = rest
        self._id = id
        self._as_dict = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.delete()

    @property
    def url(self):
        return f"{type(self).ENDPOINT}{self.id}/"

    @property
    def as_dict(self):
        if not self._as_dict:
            self._as_dict = self.fetch()
        return self._as_dict

    @property
    def id(self):
        return self._id

    def delete(self):
        self._rest.delete(self.url)

    def refresh(self):
        self._as_dict = None

    def fetch(self):
        self._as_dict = self._rest.get(self.url)
        return self._as_dict

    @property
    def exists(self):
        try:
            self.fetch()
            return True
        except Exception as e:
            if "404" in str(e):
                return False
            raise e

    def update(self, **kwargs):
        self._rest.patch(self.url, **kwargs)
        self.refresh()

    @classmethod
    def make(cls, rest, **kwargs):
        resp = rest.post(cls.ENDPOINT, kwargs)
        return cls(rest, resp[cls.ID_FIELD])

    def get_nested_detail(self, path):
        return self._rest.get(f"{self.url}{path}/")

    def add_nested(self, path, ids=[]):
        return self._rest.patch(f"{self.url}{path}/", ids=ids)

    def remove_nested(self, path, ids=[]):
        ids_str = ','.join([str(x) for x in ids])
        return self._rest.delete(f"{self.url}{path}/", ids=ids_str)

class ProjectClient(ClientBase):
    ENDPOINT = "/projects/"
    ID_FIELD = "project_id"

    @property
    def models(self):
        return self.as_dict["models"]

    @property
    def notebooks(self):
        return self.as_dict["notebooks"]

    @property
    def name(self):
        return self.as_dict["name"]

    @property
    def created(self):
        return dateutil.parser.parse(self.as_dict["created"])

    @property
    def updated(self):
        return dateutil.parser.parse(self.as_dict["updated"])

class ModelClient(ClientBase):
    ENDPOINT = "/models/"
    ID_FIELD = "model_id"

    @property
    def project(self):
        return self.as_dict["project"]

    @property
    def name(self):
        return self.as_dict["name"]

    @property
    def datasets(self):
        return self.get_nested_detail("datasets")

    def add_datasets(self, dataset_ids):
        return self.add_nested("datasets", ids=dataset_ids)

    def remove_datasets(self, dataset_ids):
        return self.remove_nested("datasets", ids=dataset_ids)

class NotebookClient(ClientBase):
    ENDPOINT = "/notebooks/"
    ID_FIELD = "notebook_id"

class DatasetClient(ClientBase):
    ENDPOINT = "/datasets/"
    ID_FIELD = "dataset_id"

    def create_from_remote(rest, project, remote_name, destination_dir):
        resp = rest.post('/datasets/create_from_remote/', {}, id=remote_name, destination=destination_dir, project_id=project.id)
        return TaskClient(rest, resp['task_id']), DatasetClient(rest, resp['dataset_id'])

    @property
    def name(self):
        return self.as_dict["name"]

    @property
    def project(self):
        return self.as_dict["project"]

    @property
    def status(self):
        return self.as_dict["status"]

    @property
    def location(self):
        return self.as_dict["location"]

    @property
    def source_url(self):
        return self.as_dict["source_url"]

    @property
    def is_perceptilabs_sourced(self):
        return self.as_dict["is_perceptilabs_sourced"]

    @property
    def exists_on_disk(self):
        return self.as_dict["exists_on_disk"]

    @property
    def models(self):
        return self.get_nested_detail("models")

    def add_models(self, model_ids):
        return self.add_nested("models", ids=model_ids)

    def remove_models(self, model_ids):
        return self.remove_nested("models", ids=model_ids)

class TaskClient(ClientBase):
    ENDPOINT = "/tasks/"

    @property
    def so_far(self):
        return self.as_dict.get('so_far', 0)

    @property
    def state(self):
        return self.as_dict['state']

    @property
    def is_completed(self):
        return self.state == "SUCCESS"

    @property
    def is_started(self):
        return self.state == "STARTED"
