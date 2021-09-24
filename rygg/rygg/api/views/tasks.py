from django.http import HttpResponseNotFound
from rest_framework import viewsets
from rest_framework.response import Response

from rygg.celery import app as celery_app
from rygg.settings import IS_CONTAINERIZED
from rygg.tasks import get_task_status, cancel_task

class TaskViewSet(viewsets.GenericViewSet):
    def retrieve(self, request, pk=None):
        info = get_task_status(pk)

        if not info:
            return HttpResponseNotFound()

        return Response(info)

    def destroy(self, request, pk=None):
        cancel_task(pk)
        return Response()
