from django.urls import path, re_path
from django.views.generic import TemplateView
from django_http_exceptions import HTTPExceptions
from rest_framework.decorators import api_view
from django.http import HttpResponse
from static_file_server.settings import IS_CONTAINERIZED
import os

class TokenView(TemplateView):
    template_name = 'index.html'

    def dispatch(self, request, *args, **kwargs):
        token = request.GET.get("token") or os.getenv("PL_FILE_SERVING_TOKEN")
        ret = super().dispatch(request, *args, **kwargs)
        if token:
            ret.set_cookie("fileserver_token", value=token, samesite="Lax")
        return ret

# TODO: this needs to be replaced by the openshift operator setting the PL_xyz._URL variables in the pods
def other_url(request, variable_name, replacement_str):
    from_env = os.getenv(variable_name, "")
    if from_env or not IS_CONTAINERIZED:
        return from_env

    my_host = request.get_host().split(':')[0]
    other_host = my_host.replace("frontend", replacement_str)
    scheme = request.scheme if replacement_str != "core" else "ws"
    return f"{scheme}://{other_host}"

@api_view(["GET"])
def kernel_url(request):
    return HttpResponse(other_url(request, "PL_KERNEL_URL", "core"))

@api_view(["GET"])
def fileserver_url(request):
    return HttpResponse(other_url(request, "PL_FILESERVER_URL", "fileserver"))

@api_view(["GET"])
def rygg_url(request):
    return HttpResponse(other_url(request, "PL_RYGG_URL", "rygg"))

urlpatterns = [
    re_path('kernel_url', kernel_url),
    re_path('fileserver_url', fileserver_url),
    re_path('rygg_url', rygg_url),
    re_path('', TokenView.as_view()),
]
