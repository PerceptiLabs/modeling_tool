from fileserver.api.views.util import json_response
from fileserver import __version__
from rest_framework.decorators import api_view

@api_view(["GET"])
def version(request):
    return json_response({"version": __version__})
