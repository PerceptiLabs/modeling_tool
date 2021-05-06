from fileserver.api.interfaces.discourse_topic import CreateDiscourseAPI
from fileserver.api.models.discourse import create_topic
from rest_framework.decorators import api_view
from fileserver.api.exceptions import UserError
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

def connect_to_discourse(username,api_key):
    return CreateDiscourseAPI(username,api_key)

@api_view(['POST'])
def discourse_issue(request):
    
    as_dict = request_as_dict(request)

    api_key = get_required_body_param("api_key", as_dict)
    username = get_required_body_param("username", as_dict)
    title = as_dict.get("title")
    body = as_dict.get("body")
    images = as_dict.get("images")

    try:
        api = connect_to_discourse(username,api_key)
        response = create_topic(api, title, body, images)

        return_response = {"topic_id": response[0], "topic_slug": response[1]}
            #Frontend can create issue URL using this <forumURL>/t/topic_slug/topic_id 
        return HttpResponse(json.dumps(return_response), content_type="application/json")
    except ValueError as e:
        raise HTTPExceptions.BAD_REQUEST.with_content(e)