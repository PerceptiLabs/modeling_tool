from retrying import retry

def assert_eventually(fn, *fn_args, **retry_kwargs):
    @retry(**retry_kwargs)
    def check():
        assert fn(*fn_args)

    check

def subdict(d, *keys):
    keyset = set(keys)
    return {k:v for k,v in d.items() if k in keyset}

def assert_is_subdict(l, r, *keys):
    assert subdict(l, *r.keys()) == r

def has_expected_files(rest, expected):
    upload_path = rest.get("/upload_dir")["path"]
    assert upload_path

    got = rest.get("/directories/get_folder_content", path=upload_path)
    return set(expected) <= set(got["files"])

def assert_dict_lists_equal(l, r, key):
    def dict_by_id(items):
        return {d[key] : d for d in items}

    assert dict_by_id(l) == dict_by_id(r)

