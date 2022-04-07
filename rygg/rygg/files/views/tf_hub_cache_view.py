from rest_framework.decorators import api_view

from rygg.files.views.util import json_response
from rygg.settings import tf_hub_cache_dir


@api_view(["GET"])
def get_tf_hub_cache_dir(request):
    resolved_path = tf_hub_cache_dir()
    return json_response({"tf_hub_cache_dir": resolved_path})
