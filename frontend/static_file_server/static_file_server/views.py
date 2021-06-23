from static_file_server import __version__
from django.urls import path, re_path
from django.views.generic import TemplateView
from django_http_exceptions import HTTPExceptions
from django.conf import settings
from rest_framework.decorators import api_view
from django.http import HttpResponse
from static_file_server.settings import IS_CONTAINERIZED
import os, requests, json
from websocket import create_connection
from rest_framework.response import Response

def _make_header_sentinel(header_as_utf):
    header_len = len(header_as_utf)
    if header_len == 256:
        return (0, header_len)
    return (header_len // 256, header_len % 256)

def _create_request():
    data = "{\"receiver\": 2021,\"action\": \"version\",\"value\": \"\",\"instanceId\": \"c3RhdGljIGZpbGUgc2VydmVy\"}"
    data_utf = data.encode(encoding='UTF-8')

    header = {
            "byteorder": 'little',
            "content-type": 'text/json',
            "content-encoding": 'utf-8',
            "content-length": len(data_utf),
          }

    json_header = json.dumps(header)
    header_utf = json_header.encode(encoding='UTF-8')
    header_len = len(header_utf)

    first_byte, second_byte = _make_header_sentinel(header_utf)
    response = bytearray()
    response.append(first_byte)
    response.append(second_byte)
    response.extend(header_utf)
    response.extend(data_utf)

    return response

# TODO: this needs to be replaced by the openshift operator setting the PL_xyz._URL variables in the pods
def other_url(request, variable_name, replacement_str):
    from_env = os.getenv(variable_name, "")
    if from_env or not IS_CONTAINERIZED:
        return from_env

    my_host = request.get_host().split(':')[0]
    other_host = my_host.replace("frontend", replacement_str)
    scheme = request.scheme if replacement_str != "core" else "ws"
    return f"{scheme}://{other_host}"

def check_version(request, variable_name, replacement_str, api_url):
    piece_url = other_url(request, variable_name, replacement_str)
    
    if not piece_url and replacement_str == "rygg":
        piece_url = settings.RYGG_URL
    url = f"{piece_url}/{api_url}"
    
    if replacement_str == "fileserver":
        if not piece_url:
            piece_url = settings.FILESERVER_URL
        token = request.query_params.get('token')
        url = f"{piece_url}/{api_url}?token={token}"
    
    response = requests.get(url, headers={}, data={})
    json_response = json.loads(response.content)

    is_ok = json_response['version'] == __version__

    json_str = json.dumps({"version": is_ok})
    return HttpResponse(json_str, content_type="application/json")

def check_kernel_version(request, variable_name, replacement_str):
    url = other_url(request, variable_name, replacement_str)
    if not url:
        url = settings.KERNEL_URL
    ws = create_connection(url)
    request_version = _create_request()
    ws.send_binary(request_version)
    response =  ws.recv_frame()
    ws.close()
    # print(response)
    body = response.data
    body_as_json = json.loads(body)
    is_ok = body_as_json['body']['content'] == __version__

    json_str = json.dumps({"version": is_ok})
    return HttpResponse(json_str, content_type="application/json")


class TokenView(TemplateView):
    template_name = 'index.html'

    def dispatch(self, request, *args, **kwargs):
        token = request.GET.get("token") or os.getenv("PL_FILE_SERVING_TOKEN")
        ret = super().dispatch(request, *args, **kwargs)
        if token:
            ret.set_cookie("fileserver_token", value=token, samesite="Lax")
        return ret

@api_view(["GET"])
def rendering_kernel_url(request):
    return HttpResponse(other_url(request, "PL_RENDERING_KERNEL_URL", "core"))
    
@api_view(["GET"])
def kernel_url(request):
    return HttpResponse(other_url(request, "PL_KERNEL_URL", "core"))

@api_view(["GET"])
def fileserver_url(request):
    return HttpResponse(other_url(request, "PL_FILESERVER_URL", "fileserver"))

@api_view(["GET"])
def rygg_url(request):
    return HttpResponse(other_url(request, "PL_RYGG_URL", "rygg"))

@api_view(["GET"])
def rygg_version(request):
    return check_version(request, "PL_RYGG_URL", "rygg", "app/version")

@api_view(["GET"])
def keycloak_url(request):
    ret = other_url(request, "PL_KEYCLOAK_URL", "")
    return HttpResponse(ret)

@api_view(["GET"])
def fileserver_version(request):
    return check_version(request, "PL_FILESERVER_URL", "fileserver", "version")

@api_view(["GET"])
def kernel_version(request):
    return check_kernel_version(request, "PL_KERNEL_URL", "kernel")

@api_view(["HEAD"])
def is_enterprise(request):
    code = 204 if IS_CONTAINERIZED else 404
    return Response(status=code)

