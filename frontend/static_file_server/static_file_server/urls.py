from django.urls import path, re_path
from django.views.generic import TemplateView
from django_http_exceptions import HTTPExceptions
from rest_framework.decorators import api_view
from django.http import HttpResponse
import os

class TokenView(TemplateView):
    template_name = 'index.html'

    def dispatch(self, request, *args, **kwargs):
        token = request.GET.get("token") or os.getenv("PL_FILE_SERVING_TOKEN")
        ret = super().dispatch(request, *args, **kwargs)
        if token:
            ret.set_cookie("fileserver_token", value=token, samesite="Lax")
        return ret

@api_view(["GET"])
def kernel_url(request):
    return HttpResponse(os.getenv("PL_KERNEL_URL", ""))

@api_view(["GET"])
def fileserver_url(request):
    return HttpResponse(os.getenv("PL_FILESERVER_URL", ""))

@api_view(["GET"])
def rygg_url(request):
    return HttpResponse(os.getenv("PL_RYGG_URL", ""))

urlpatterns = [
    re_path('kernel_url', kernel_url),
    re_path('fileserver_url', fileserver_url),
    re_path('rygg_url', rygg_url),
    re_path('', TokenView.as_view()),
]
