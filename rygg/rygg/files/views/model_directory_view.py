from django_http_exceptions import HTTPExceptions
from rygg.files.views.util import (
        get_path_param,
        get_paged_iter,
        json_response,
        )
from rygg.files.models.model_directory import get_contents
from rest_framework.decorators import api_view

@api_view(["GET", "HEAD"])
def get_modeldirectory(request):
    full_path = get_path_param(request)
    try:
        # we'll cheat by getting the contents generator and never iterating it.
        seq = get_contents(full_path)
        if seq == None:
            raise HTTPExceptions.NO_CONTENT
    except ValueError as e:
        raise HTTPExceptions.BAD_REQUEST.with_content(e)

    return json_response({"path": full_path})

@api_view(["GET"])
def modeldirectory_tree(request):
    full_path = get_path_param(request)

    try:
        paths_iter = get_contents(full_path)
    except ValueError as e:
        raise HTTPExceptions.BAD_REQUEST.with_content(e)

    page, contents = get_paged_iter(paths_iter, request)

    response = {
            "path": full_path,
            "page": page,
            "contents": contents,
            }

    return json_response(response)


