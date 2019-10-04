import copy
import pprint
import logging


log = logging.getLogger(__name__)


class ExecutionScope:
    def __init__(self, globals_, locals_=None):
        self._globals = copy.copy(globals_)
        self._locals = dict() if locals_ is None else copy.copy(locals_)
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    @property
    def locals(self):
        return copy.copy(self._locals)    

    @property
    def globals(self):
        return copy.copy(self._globals)

    def run(self, code):
        try:
            exec(code, self._globals, self._locals)
        except:
            text  = "Exception when executing code:\n"
            text += "------------------------------\n"
            text += code
            text += "------------------------------\n"
            #text += "Globals:\n"
            #text += pprint.pformat(self._globals)
            text += "Locals:\n"
            text += pprint.pformat(self._locals)
            log.error(text)
            log.exception("Exception:")            
            raise

    def set_local(self, key, value):
        self._locals[key] = copy.copy(value)
