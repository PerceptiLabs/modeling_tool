import os
import uuid
import queue
import inspect
import traceback
import sentry_sdk

from perceptilabs.utils import add_line_numbering


def traceback_from_exception(exception):
    tb_obj = traceback.TracebackException(
        exception.__class__,
        exception,
        exception.__traceback__
    )
    text = "".join(tb_obj.format())
    return text


class Issue:
    def __init__(self, message, exception=None):
        self._message = message
        self._exception = exception
        self.internal_message = None
        self.frontend_message = None
        
    def __enter__(self):
        frame = inspect.stack()[1]
        caller = inspect.getframeinfo(frame[0])
        module = inspect.getmodule(frame[0])
        location = f'{module.__name__}:{caller.lineno}'
        
        self.frontend_message = f"Internal error in {location}. This will be reported as a bug."
        self.internal_message = self._message + f" (issue origin: {location})"
        
        if self._exception:
            self.internal_message += "\n" + traceback_from_exception(self._exception)
            
        return self
    
    def __exit__(self, type, value, tb):
        pass

    
class IssueHandler:
    def __init__(self):
        self._errors = queue.Queue()        
        self._warnings = queue.Queue()

    @staticmethod
    def create_issue(message, exception=None):
        return Issue(message, exception)

    def put_error(self, message):
        self._errors.put(message)

    def put_warning(self, message):
        self._warnings.put(message)

    def _pop_messages(self, queue):
        message_list = []
        while not queue.empty():
            message = queue.get(timeout=0.05)
            message_list.append(message)
        return message_list
        
    def pop_errors(self):
        return self._pop_messages(self._errors)

    def pop_warnings(self):
        return self._pop_messages(self._warnings)    

        
class UserlandError:
    def __init__(self, layer_id, layer_type, line_number, message, code=None):
        self.layer_id = layer_id
        self.layer_type = layer_type
        self.line_number = line_number
        self.message = message
        self.code = code

    def format(self, with_code=False):
        text = f'Error in layer {self.layer_id} [{self.layer_type}]. '
        
        if line_number:
            text += f'Line: {self.line_number}'
        
        if with_code and self.code is not None:
            text += '\n' + add_line_numbering(self.code)
            
        text += '\n' + self.message
        return text

        
if __name__ == "__main__":
    issues = IssueHandler()

    def fn():
        raise RuntimeError("Unexpected error!!")        
    
    try:
        fn()
    except Exception as e:

        with issues.create_issue('error in block', e) as issue:
            issues.put_error(issue.frontend_message)
            print(issue.internal_message)

    x = issues.pop_errors()
    print(x)
    
        





