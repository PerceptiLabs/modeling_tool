from django.urls import path, re_path
from django.views.generic import TemplateView
from django_http_exceptions import HTTPExceptions
from rest_framework.decorators import api_view
from django.http import HttpResponse
from rest_framework.response import Response
from static_file_server.settings import IS_CONTAINERIZED
import os
from static_file_server.views import (
    fileserver_version, 
    kernel_version, 
    rygg_version, 
    rygg_url, 
    kernel_url,
    rendering_kernel_url,
    fileserver_url,
    keycloak_url,
    is_enterprise,
    TokenView
    )


urlpatterns = [
    re_path('kernel_url', kernel_url),
    re_path('rendering_kernel_url', rendering_kernel_url),
    re_path('keycloak_url', keycloak_url),
    re_path('fileserver_url', fileserver_url),
    re_path('rygg_url', rygg_url),
    re_path('is_enterprise', is_enterprise),
    re_path('rygg_version', rygg_version),
    re_path('fileserver_version', fileserver_version),
    re_path('kernel_version', kernel_version),
    re_path('', TokenView.as_view()),
]
