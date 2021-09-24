from rygg.test_utils.timeout_decorator import timeout
from django.test import TestCase
from threading import Event
import rygg.files.utils.subprocesses as target

def gen(*arr):
    return (x for x in arr)

class SubprocessTest(TestCase):
    @timeout(0.1)
    def test_cancellable_sequence(self):
        seq = gen(1,2,3)
        cancel_token = Event()
        cancellable = target.cancelable_sequence(seq, cancel_token)

        def iterate_and_cancel():
            for x in cancellable:
                cancel_token.set()

        self.assertRaises(target.CanceledError, iterate_and_cancel)

