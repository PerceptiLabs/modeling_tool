from django.test import TestCase
from django_http_exceptions import HTTPExceptions
from rygg.files.views import util as target
from unittest.mock import Mock, NonCallableMagicMock, patch
import os
import shutil
import tempfile
import unittest

from rygg.api.models import Project
from rygg.files.tests.utils import TempFileTester

PROJECT_ID = None


def setUpModule():
    global PROJECT_ID

    p = Project()
    p.save()
    PROJECT_ID = p.project_id


def tearDownModule():
    Project.objects.filter(pk=PROJECT_ID).delete()


class GetPathParamEnterprise(TempFileTester, TestCase):
    def test_good_checks_params_and_passes_through_to_translate(self):
        mock = Mock()
        mock.query_params = {"project_id": PROJECT_ID, "path": "a"}

        mock_project = Mock()
        mock_project.project_id = PROJECT_ID

        with patch("rygg.files.paths.translate_path_from_user") as translate, patch(
            "rygg.api.models.Project.get_by_id"
        ) as get_by_id:

            get_by_id.return_value = mock_project

            translate.return_value = "ret"
            resp = target.get_path_param(mock)
            self.assertEqual(resp, "ret")
            translate.assert_called_once_with("a", PROJECT_ID)

    def test_fails_without_project_id(self):
        mock = Mock()
        mock.query_params = {"path": "a"}
        self.assertRaises(HTTPExceptions.BAD_REQUEST, target.get_path_param, mock)

    def test_fails_without_path(self):
        mock = Mock()
        mock.query_params = {"project_id": PROJECT_ID}
        self.assertRaises(HTTPExceptions.BAD_REQUEST, target.get_path_param, mock)
