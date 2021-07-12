from rest_framework.decorators import api_view
from rygg.files.views.util import json_response
import urllib.request
import ssl

@api_view(["GET"])
def is_url_reachable(request):
  url = request.GET.get('path')
  requestContext = ssl._create_unverified_context()

  try:
      urllib.request.urlopen(url, context=requestContext).getcode()
      return json_response({"response_code": 200})
  except:
      return json_response({"response_code": 500})
