import json
import requests
from urllib.parse import urlencode

headers = {"content-type": "application/json", "accept": "application/json"}

class RyggRest():
    def __init__(self, base_url, token):
        self._base_url = base_url.strip("/")
        self._token = token

    def check(self):
        self.get("/app/version")["version"]

    def post(self, relpath, doc, **urlparams):
        payload = json.dumps(doc)
        query = self.build_query(relpath, **urlparams)
        resp = requests.post(query, data=payload, headers=headers)
        if not resp.ok:
            raise Exception(f"Error status {resp.status_code} received. Content: {resp.content}")
        return None if not resp.content else resp.json()

    def post_file(self, relpath, file_path, file_name, **urlparms):
        files = {"file_uploaded": (file_name, open(file_path, "rb"), "application/octet-stream")}
        url = self.build_query(relpath)
        resp = requests.post(url, files=files, data={"token": self._token, **urlparms})
        if not resp.ok:
            raise Exception(f"Error status {resp.status_code} received. Content: {resp.content}")
        return None if not resp.content else resp.json()

    def build_query(self, relpath, **parms):
        encoded_parms = urlencode({"token": self._token, **parms})
        return f"{self._base_url}{relpath}?{encoded_parms}"

    def assert_success(self, resp):
        if not resp.ok:
            raise Exception(f"Error status {resp.status_code} received")

    def head(self, relpath, **parms):
        query = self.build_query(relpath, **parms)
        resp = requests.head(query, headers=headers)
        self.assert_success(resp)
        return resp.status_code == 204

    def get(self, relpath, **parms):
        query = self.build_query(relpath, **parms)
        resp = requests.get(query, headers=headers)
        self.assert_success(resp)
        return None if not resp.content else resp.json()


    def patch(self, relpath, **kwargs):
        payload = json.dumps(kwargs)
        resp = requests.patch(f"{self._base_url}{relpath}", data=payload, headers=headers)
        self.assert_success(resp)
        return None if not resp.content else resp.json()

    def delete(self, relpath, **urlparms):
        query = self.build_query(relpath, **urlparms)
        resp = requests.delete(query, headers=headers)
        self.assert_success(resp)
        return None if not resp.content else resp.json()
