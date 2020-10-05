from fileserver.api.views.util import json_response
from fileserver import __version__
from rest_framework.decorators import api_view
from django_http_exceptions import HTTPExceptions

@api_view(["GET"])
def version(request):
    return json_response({"version": __version__})
