from retrying import retry
import os

def assert_eventually(fn, *fn_args, **retry_kwargs):
    @retry(**retry_kwargs)
    def check():
        assert fn(*fn_args)

    check()

def subdict(d, *keys):
    keyset = set(keys)
    return {k:v for k,v in d.items() if k in keyset}

def assert_is_subdict(l, r, *keys):
    assert subdict(l, *r.keys()) == r

def has_expected_files(rest, expected, root):
    upload_path = rest.get("/upload_dir")["path"]
    assert upload_path

    path = upload_path
    if root:
        path = os.path.join(upload_path, root)

    got = rest.get("/directories/get_folder_content", path=path)
    return set(expected) <= set(got["files"])

def task_is_complete(rest, task_id):
    resp = rest.get(f"/tasks/{task_id}/")
    return resp["state"] == "SUCCESS"


def assert_dict_lists_equal(l, r, key):
    def dict_by_id(items):
        return {d[key] : d for d in items}

    assert dict_by_id(l) == dict_by_id(r)

