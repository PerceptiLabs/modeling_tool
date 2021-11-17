from rest_framework.response import Response
from django_http_exceptions import HTTPExceptions
import json
import os
import platform

from rygg.api.models import Project
from rygg.files.paths import translate_path_from_user, PathNotAvailable
from rygg.settings import IS_CONTAINERIZED
import rygg.files.paths

def get_required_param(request, param):
    qp = request.query_params
    if not qp.__contains__(param):
        raise HTTPExceptions.BAD_REQUEST.with_content(f"Missing {param} parameter")
    return qp[param]

def get_optional_int_param(request, param, default):
    as_str = get_optional_param(request, param, default)
    try:
        return int(as_str)
    except ValueError:
        raise HTTPExceptions.BAD_REQUEST.with_content(f"{param} must be an integer.")

def get_optional_param(request, param, default):
    qp = request.query_params
    return qp[param] if qp.__contains__(param) else default

# Extracts the required "path" parameter from the request and validates it
# Then passes through to translate_path_from_user where all of the path logic is done
def get_path_param(request):
    path = get_required_param(request, "path")
    if IS_CONTAINERIZED and path.startswith("~"):
        raise HTTPExceptions.BAD_REQUEST.with_content("Home directory isn't supported.")
    project_id = get_project_id_from_request(request)
    try:
        return rygg.files.paths.translate_path_from_user(path, project_id)
    except PathNotAvailable as e:
        raise HTTPExceptions.NOT_FOUND.with_content(e)



def get_project_id_from_request(request):
    project_id = int(get_required_param(request, "project_id"))
    if not Project.objects.filter(pk=project_id).exists():
        raise HTTPExceptions.NOT_FOUND.with_content(f"Project {project_id} does not exist")
    return project_id

def json_response(response_content):
    return Response(response_content, content_type="application/json")


def make_path_response(full_path):
    return json_response({"path": full_path})


def request_as_dict(request):
    # we can't decode the body as utf-8 json then it's a bad request
    try:
        ret = json.loads(request.body, encoding="utf-8")
        as_utf8 = request.body.decode("utf-8")
        return json.loads(as_utf8, encoding="utf-8")
    except:
        raise HTTPExceptions.BAD_REQUEST.with_content("Invalid json request")

def protect_read_only_enterprise_field(request, field_name):
    if IS_CONTAINERIZED:
        as_dict = request_as_dict(request)
        if field_name in request_as_dict(request):
            raise HTTPExceptions.BAD_REQUEST.with_content(f"{field_name} is read-only")

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

