from rygg.test_utils.timeout_decorator import timeout
from django.test import TestCase
from more_itertools import consume
from unittest.mock import Mock, call
import rygg.files.utils.sequences as target

class SequencesTest(TestCase):
    @timeout(0.1)
    def test_observe_progress(self):
        num = 1000
        r = (x for x in range(num))
        mock = Mock()

        # expect updates of 1%
        expected = [call(num, x*10) for x in range(int(num/10))]

        observed = target.observe_progress(num, r, mock.method)
        consume(observed)

        mock.method.assert_has_calls(expected)
