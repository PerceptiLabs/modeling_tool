from django.test import TestCase
from rygg.api.models import  Project

class ProjectTestCase(TestCase):
    def setUp(self):
        Project.objects.create(name="The Project")

    def test_noop(self): # ATM, projects do nothing, so just noop
        pass
