from queue import Queue
import logging
import traceback
# import sentry_sdk
from collections import namedtuple
from abc import ABC, abstractmethod
import copy

from perceptilabs.core_new.session import LayerSession

log = logging.getLogger(__name__)


class LayerSessionAbort(Exception):
    pass

class LayerErrorHandler(ABC):
    @abstractmethod
    def handle_run_error(self, session: LayerSession, exception: Exception):
        raise NotImplementedError

    def _format_code(self, code: str, error_line: int=None):
        code_lines = code.split('\n')
        code_lines = ["%d %s" % (i, l) for i, l in enumerate(code_lines, 1)]
        code = "\n".join(code_lines)
        return code        

    # def _store_error(self, layer_id, short_descr, long_descr, line_number):
    #     error = ErrorDescription(short_descr, long_descr, line_number)
    #     self._errors[layer_id] = error
    #     log.info("Handled error in layer {}. Description: \n{}".format(layer_id, error.long_descr))

    def _get_error_line(self, exception: Exception):
        tb_list=traceback.extract_tb(exception.__traceback__)
        line_number=None
        for i in tb_list:
            if i[2]=="<module>":
                line_number=i[1]

        return line_number

    def _log_error(self, session: LayerSession, exception: Exception, error_line: int=None):
        code_lines = session.code.split('\n')
        code_lines = ["  %d %s" % (i, l) for i, l in enumerate(code_lines, 1)]

        if error_line is not None:
            code_lines[error_line-1] = '->' + code_lines[error_line-1][2:]
        code = "\n".join(code_lines)
        
        message  = "%s when running layer session %s:\n" % (repr(exception), session.layer_id)
        message += "%s\n" % code
        message += "\n"
        message += "".join(traceback.format_tb(exception.__traceback__))
        log.info(message)

    def reset(self):
        pass

    
ErrorDescription = namedtuple('ErrorDescription', ['error_message', 'error_line'])


class LightweightErrorHandler(LayerErrorHandler):
    def __init__(self):
        self.reset()

    def reset(self):
        self._dict = {}
    
    def handle_run_error(self, session: LayerSession, exception: Exception):
        if isinstance(exception, SyntaxError):
            self._handle_syntax_error(session, exception)
        else:
            self._handle_other_errors(session, exception)

    def _handle_syntax_error(self, session: LayerSession, exception: Exception):
        tbObj = traceback.TracebackException(exception.__class__,
                                             exception,
                                             exception.__traceback__)

        descr = "".join(tbObj.format_exception_only())
        self._dict[session.layer_id] = ErrorDescription(descr, str(tbObj.lineno) or "?")
        self._log_error(session, exception, int(tbObj.lineno))
        
    def _handle_other_errors(self, session: LayerSession, exception: Exception):                    
        error_class = exception.__class__.__name__
        line_number = self._get_error_line(exception)
        descr = "%s at line %d: %s" % (error_class, line_number, exception)

        self._dict[session.layer_id] = ErrorDescription(descr, str(line_number))
        self._log_error(session, exception, int(line_number))        
        
    def to_dict(self):
        return copy.copy(self._dict)

    def __contains__(self, id_):
        return id_ in self._dict

    def __getitem__(self, id_):
        return self._dict[id_]
    
        
class CoreErrorHandler(LayerErrorHandler):
    def __init__(self, error_queue: Queue):
        self._error_queue = error_queue
    
    def handle_run_error(self, session: LayerSession, exception: Exception):
        line_number = self._get_error_line(exception)

        self._log_error(session, exception, line_number)
        self._put_message_on_queue(session, exception)
        # sentry_sdk.capture_exception(exception)

        raise LayerSessionAbort() 
    
    def _put_message_on_queue(self, session: LayerSession, exception: Exception):
        tb_obj = traceback.TracebackException(exception.__class__,
                                              exception,
                                              exception.__traceback__)

        frames = [f for f in traceback.extract_tb(exception.__traceback__) \
                  if f.filename == '<string>']

        message  = "Error in layer {} [{}]\n\n".format(session.layer_id, session.layer_type)
        message += "Traceback (most recent call last):\n"        
        for summary in frames:
            message += "  Line {}, in {}\n".format(summary.lineno, summary.name)
            message += "    {}\n".format(session.code.split('\n')[summary.lineno - 1])
        message += "\n" + "".join(tb_obj.format_exception_only())
        self._error_queue.put(message)
        
    
    





    

    

    

