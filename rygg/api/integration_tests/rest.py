import json
import requests

host = "localhost"
port = 8000
api = f"http://{host}:{port}"
headers = {"content-type": "application/json", "accept": "application/json"}


def check():
    requests.get(api).json()


def post(relpath, **kwargs):
    payload = json.dumps(kwargs)
    resp = requests.post(f"{api}{relpath}", data=payload, headers=headers)
    if not resp.ok:
        raise Exception(f"Error status {resp.status_code} received")
    return None if not resp.content else resp.json()


def get(relpath):
    resp = requests.get(f"{api}{relpath}", headers=headers)
    if not resp.ok:
        raise Exception(f"Error status {resp.status_code} received")
    return None if not resp.content else resp.json()


def patch(relpath, **kwargs):
    payload = json.dumps(kwargs)
    resp = requests.patch(f"{api}{relpath}", data=payload, headers=headers)
    if not resp.ok:
        raise Exception(f"Error status {resp.status_code} received: {resp.json()}")
    return None if not resp.content else resp.json()

def delete(relpath):
    resp = requests.delete(f"{api}{relpath}", headers=headers)
    if not resp.ok:
        raise Exception(f"Error status {resp.status_code} received: {resp.json()}")
    return None if not resp.content else resp.json()
