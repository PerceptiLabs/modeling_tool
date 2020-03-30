import uuid
import queue
import traceback


class Issue:
    def __init__(self, message, exception=None):
        self._message = message
        self._exception = exception
        self.internal_message = None
        self.frontend_message = None
        
    def __enter__(self):
        id_ = uuid.uuid4().hex
        self.frontend_message = f"Internal error. This error will be reported. (id: {id_})"
        self.internal_message = self._message + f" (internal error id: {id_})"
        
        if self._exception:
            tb_obj = traceback.TracebackException(
                self._exception.__class__,
                self._exception,
                self._exception.__traceback__
            )
            self.internal_message += "\n" + "".join(tb_obj.format())
            
        return self
    
    def __exit__(self, type, value, tb):
        pass

    
class IssueHandler:
    def __init__(self):
        self._errors = queue.Queue()        
        self._warnings = queue.Queue()

    @staticmethod
    def format_issue(message, exception=None):
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
        

if __name__ == "__main__":
    issues = IssueHandler()

    def fn():
        raise RuntimeError("Unexpected error!!")        
    
    try:
        fn()
    except Exception as e:

        with issues.format_issue('error in block', e) as issue:
            issues.put_error(issue.frontend_message)
            print(issue.internal_message)

    x = issues.pop_errors()
    print(x)
    
        





