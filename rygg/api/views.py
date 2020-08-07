import json
from django.http import HttpResponse, HttpResponseServerError
from django.conf import settings
from rest_framework import viewsets
from rest_framework import permissions
from rygg.api.models import Project, Model, Notebook
from rygg.api.serializers import ProjectSerializer, ModelSerializer, NotebookSerializer
from rygg.api.services import GitHubService

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("-project_id")
    serializer_class = ProjectSerializer


class ModelViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer

class NotebookViewSet(viewsets.ModelViewSet):
    queryset = Notebook.objects.all()
    serializer_class = NotebookSerializer

class IssuesViewSet(viewsets.ViewSet):

    def create(self, request):

        requestPayload = json.loads(request.body.decode("utf-8"))
        
        githubService = GitHubService(settings);        

        try:
            result = githubService.createIssue(**requestPayload)

            response = HttpResponse(result.text, content_type='application/json')
            return response

        except:
            return HttpResponseServerError()
        
        
