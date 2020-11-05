from rygg.api.models import Project, Model, Notebook, FileLink
from rest_framework import serializers


class NotebookSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    location = serializers.SerializerMethodField()

    class Meta:
        model = Notebook
        fields = ["notebook_id", "project", "name", "created", "updated", "location"]

    def create(self, validated_data):

        request = self.context.get('request', {})
        location = request.data.get('location', '')

        filelink = FileLink.objects.create(resource_locator=location)
        filelink.save()
        
        notebook = Notebook.objects.create(**validated_data)
        notebook.filelink = filelink
        notebook.save()

        return notebook

    def update(self, instance, validated_data):
        
        request = self.context.get('request', {})
        location = request.data.get('location', '')

        filelink = instance.filelink

        if filelink.resource_locator != location:
            filelink.resource_locator = location
            filelink.save()

        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

    def get_location(self, obj):
        return obj.filelink.resource_locator



class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    models = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    notebooks = NotebookSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        fields = ["project_id", "name", "default_directory", "created", "updated", "models", "notebooks"]

class ModelSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Model
        fields = ["model_id", "project", "name", "created", "updated", "saved_by", "location", "saved_version_location"]
