from django.http import HttpResponse
from django_http_exceptions import HTTPExceptions
from fileserver.api.models.directory import resolve_dir
import chardet
import json
import os
import platform

def get_required_param(request, param):
    qp = request.query_params
    if not qp.__contains__(param):
        raise HTTPExceptions.BAD_REQUEST.with_content(f"Missing {param} parameter")
    return qp[param]

def get_optional_param(request, param, default):
    qp = request.query_params
    return qp[param] if qp.__contains__(param) else default

IS_WIN = platform.system().lower().startswith("win")

def get_full_path(raw_path):
    resolved = resolve_dir(raw_path)
    with_root = resolved if IS_WIN else os.path.join("/", resolved)
    return os.path.abspath(with_root)

# Extracts the required "path" parameter from the request and validates it
def get_path_param(request):
    raw_path = get_required_param(request, "path")
    return get_full_path(raw_path)

def json_response(response_content):
    response_json = json.dumps(response_content)
    return HttpResponse(response_json, content_type="application/json")


def make_path_response(full_path):
    return json_response({"path": full_path})


def request_as_dict(request):
    # we can't decode the body as utf-8 json then it's a bad request
    try:
        ret = json.loads(request.body, encoding="utf-8")
        as_utf8 = request.body.decode("utf-8")
        ret = json.loads(as_utf8, encoding="utf-8")
        
        return ret
    except:
        raise HTTPExceptions.BAD_REQUEST.with_content("Invalid json request")

def get_page(seq, page=1, per=100):
    if per < 1:
        raise ValueError(f"per must be greater than 0")
    if page < 1:
        raise ValueError(f"page must be greater than 0")
    start = (page-1) * per
    end = start + per
    return seq[start:end]

def get_required_body_param(name, body_as_dict):
    ret = body_as_dict.get(name)
    if ret == None:
        raise HTTPExceptions.BAD_REQUEST.with_content(f"Request body missing required parameter {name}")
    return ret

def get_paged_iter(seq, request):
    page = get_optional_param(request, "page", 1)
    per = get_optional_param(request, "per", 100)
    if seq == None:
        raise HTTPExceptions.NO_CONTENT

    return (page, get_page(seq, page=page, per=per))

def get_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw = file.read(32) # at most 32 bytes are returned
        return chardet.detect(raw)['encoding']

def make_file_content_response(request, file_path):

    num_rows = get_optional_param(request, "num_rows", 4) #5 rows, 0 indexed
    row_count = 0

    print(file_path, num_rows)

    row_contents = []

    encoding=get_encoding(file_path)

    try:
        with open(file_path, 'r', encoding=encoding) as reader:
            line = reader.readline()
            while line != '' and row_count < num_rows:
                row_contents.append(line)
                line = reader.readline()
                row_count += 1
    except Exception as err:
        raise('Error when reading file contents')

    return json_response({"file_contents": row_contents})
