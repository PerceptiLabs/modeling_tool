from django.http import HttpResponse
from rest_framework import viewsets
import json

from rygg.api.services import GitHubService

class IssuesViewSet(viewsets.ViewSet):
    def create(self, request):
        requestPayload = json.loads(request.body.decode("utf-8"))
        githubService = GitHubService();

        result = githubService.createIssue(**requestPayload)
        return HttpResponse(result.text, content_type='application/json')
