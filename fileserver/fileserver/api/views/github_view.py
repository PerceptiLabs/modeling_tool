from collections.abc import  Iterable
from fileserver.api.interfaces.github_export import RepoExporterAPI
from fileserver.api.interfaces.github_issue import CreateIssueAPI
from rest_framework.decorators import api_view
from fileserver.api.models.github import export_repo_basic, import_repo, create_issue
from fileserver.api.views.util import (
        get_required_param,
        get_path_param,
        request_as_dict,
        get_required_body_param,
        get_full_path,
        )
from django_http_exceptions import HTTPExceptions
from django.http import HttpResponse
import json

def connect_to_repo(token, repo_name):
    return RepoExporterAPI(token, repo_name)

@api_view(['POST'])
def github_export(request):
    full_path = get_path_param(request)
    as_dict = request_as_dict(request)

    # required
    github_token = get_required_body_param("github_token", as_dict)
    repo_name = get_required_body_param("repo_name", as_dict)
    commit_message = get_required_body_param("commit_message", as_dict)

    # optional
    include_trained = bool(as_dict.get("include_trained_model"))
    raw_data_paths = list(as_dict.get("data_path"))

    data_paths = [get_full_path(data_path) for data_path in raw_data_paths]

    try:
        api = connect_to_repo(github_token, repo_name)
        sha = export_repo_basic(api, full_path, include_trained, data_paths, commit_message=commit_message)

        response = {"sha": sha}
        return HttpResponse(json.dumps(response), content_type="application/json")
    except ValueError as e:
        raise HTTPExceptions.BAD_REQUEST.with_content(e)



@api_view(['POST'])
def github_import(request):
    path = get_required_param(request, "path")
    url = get_required_param(request, "url")
    try:
        overwrite = request.query_params.get("overwrite")
        overwrite = bool(overwrite)
    except:
        raise HTTPExceptions.BAD_REQUEST.with_content("Overwrite isn't valid")

    try:
        import_repo(path, url, overwrite=overwrite)
        response = {"path": path}
        return HttpResponse(json.dumps(response), content_type="application/json")
    except ValueError as e:
        raise HTTPExceptions.BAD_REQUEST.with_content(e)


@api_view(['POST'])
def github_issue(request):
    
    as_dict = request_as_dict(request)

    github_token = get_required_body_param("github_token", as_dict)
    issue_type = get_required_body_param("issue_type", as_dict)
    title = as_dict.get("title")
    body = as_dict.get("body")

    try:
        api = CreateIssueAPI(github_token,issue_type)
        number = create_issue(api, title, body)

        response = {"Issue Number": number}
        return HttpResponse(json.dumps(response), content_type="application/json")
    except ValueError as e:
        raise HTTPExceptions.BAD_REQUEST.with_content(e)