from django_http_exceptions import HTTPExceptions
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os

from rygg.files.exceptions import UserError
from rygg.files.interfaces.github_issue import CreateIssueAPI
from rygg.files.views.util import get_required_param, request_as_dict, get_required_body_param
import rygg.files.paths
import rygg.files.views.util

@api_view(['POST'])
def github_export(request):
    full_path = rygg.files.views.util.get_path_param(request)
    project_id = rygg.files.views.util.get_project_id_from_request(request)
    as_dict = request_as_dict(request)

    # required
    github_token = get_required_body_param("github_token", as_dict)
    repo_name = get_required_body_param("repo_name", as_dict)
    commit_message = get_required_body_param("commit_message", as_dict)
    export_type = as_dict.get("export_type")

    # optional
    include_trained = bool(as_dict.get("include_trained_model"))
    raw_data_paths = list(as_dict.get("data_path"))

    resolve_path = lambda data_path: rygg.files.paths.translate_path_from_user(data_path, project_id)

    data_paths = [resolve_path(data_path) for data_path in raw_data_paths]

    try:
        if export_type == "basic":
            sha_and_url = rygg.files.models.github.export_repo_basic(github_token, repo_name, full_path, include_trained, data_paths, commit_message=commit_message)

        elif export_type == "advanced":
            tensorfiles_list = list(as_dict.get("tensorfiles"))
            datafiles_list = list(as_dict.get("datafiles"))
            sha_and_url = rygg.files.models.github.export_repo_advanced(github_token, repo_name, full_path, tensorfiles_list, datafiles_list, data_paths, commit_message=commit_message)

        else:
            raise HTTPExceptions.BAD_REQUEST.with_content("Invaild github export type")

        response = {"sha": sha_and_url[0], "URL": sha_and_url[1]}
        return Response(response, content_type="application/json")
    except ValueError as e:
        raise HTTPExceptions.BAD_REQUEST.with_content(e)
    except UserError as e:
        raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content(e.message)



@api_view(['POST'])
def github_import(request):
    path = rygg.files.views.util.get_path_param(request)
    url = get_required_param(request, "url")
    try:
        overwrite = request.query_params.get("overwrite")
        overwrite = bool(overwrite)
    except:
        raise HTTPExceptions.BAD_REQUEST.with_content("Overwrite isn't valid")

    try:
        rygg.files.models.github.import_repo(path, url, overwrite=overwrite)
        response = {"path": path}
        return Response(response, content_type="application/json")
    except ValueError as e:
        raise HTTPExceptions.BAD_REQUEST.with_content(e)
    except UserError as e:
        raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content(e.message)
    except Exception as e:
        raise HTTPExceptions.INTERNAL_SERVER_ERROR.with_content(e.message)


@api_view(['POST'])
def github_issue(request):
    as_dict = request_as_dict(request)
    github_token = get_required_body_param("github_token", as_dict)
    issue_type = get_required_body_param("issue_type", as_dict)
    title = as_dict.get("title")
    body = as_dict.get("body")

    try:
        number = rygg.files.models.github.create_issue(github_token, issue_type, title, body)

        response = {"Issue Number": number}
        return Response(response, content_type="application/json")
    except ValueError as e:
        raise HTTPExceptions.BAD_REQUEST.with_content(e)
