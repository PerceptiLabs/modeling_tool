import json
import requests
from urllib.parse import urlencode


headers = {"content-type": "application/json", "accept": "application/json"}

class RyggRest():
    def __init__(self, base_url, token):
        self._base_url = base_url.strip("/")
        self._token = token
        self._upload_dirs = {}
        self._session = requests.Session()

    def get_upload_dir(self, project_id):
        if not project_id in self._upload_dirs:
            dir = self.get("/upload_dir", project_id=project_id)["path"]
            self._upload_dirs[project_id] = dir

        return self._upload_dirs[project_id]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._session.close()


    def check(self):
        self.get("/app/version/")["version"]
        return True

    def post(self, relpath, body_dict, **urlparams):
        payload = json.dumps(body_dict)
        query = self.build_query(relpath, **urlparams)
        resp = self._session.post(query, data=payload, headers=headers)
        if not resp.ok:
            raise Exception(f"Error status {resp.status_code} received. Content: {resp.content}")
        return None if not resp.content else resp.json()

    def post_file(self, relpath, file_path, file_name, project_id, **urlparms):
        files = {"file_uploaded": (file_name, open(file_path, "rb"), "application/octet-stream")}
        url = self.build_query(relpath, project_id=project_id)
        resp = self._session.post(url, files=files, data={"token": self._token, "project_id": project_id, **urlparms})
        if not resp.ok:
            raise Exception(f"Error status {resp.status_code} received. Content: {resp.content}")
        return None if not resp.content else resp.json()

    def build_query(self, relpath, **parms):
        encoded_parms = urlencode({"token": self._token, **parms})
        return f"{self._base_url}{relpath}?{encoded_parms}"

    def assert_success(self, resp):
        if not resp.ok:
            raise Exception(f"Error status {resp.status_code} received. Text: {resp.text}")

    def head(self, relpath, **parms):
        query = self.build_query(relpath, **parms)
        resp = self._session.head(query, headers=headers)
        self.assert_success(resp)
        return resp.status_code == 204

    def get(self, relpath, **parms):
        query = self.build_query(relpath, **parms)
        resp = self._session.get(query, headers=headers)
        self.assert_success(resp)
        return None if not resp.content else resp.json()


    def patch(self, relpath, **kwargs):
        payload = json.dumps(kwargs)
        query = self.build_query(relpath)
        resp = self._session.patch(query, data=payload, headers=headers)
        self.assert_success(resp)
        return None if not resp.content else resp.json()

    def delete(self, relpath, **urlparms):
        query = self.build_query(relpath, **urlparms)
        resp = self._session.delete(query, headers=headers)
        self.assert_success(resp)
        return None if not resp.content else resp.json()

    @property
    def is_enterprise(self):
        if not hasattr(self, "_is_enterprise"):
            self._is_enterprise = self.get("/app/is_enterprise/")["is_enterprise"]

        return self._is_enterprise
