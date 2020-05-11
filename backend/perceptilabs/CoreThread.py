import threading
import traceback
import sys
import sentry_sdk
from sentry_sdk import utils
from sentry_sdk import capture_exception
# from sentry_sdk import configure_scope
import logging


from perceptilabs.core_new.history import HistoryInputException
from perceptilabs.core_new.errors import LayerSessionAbort

log = logging.getLogger(__name__)

class CoreThread(threading.Thread):
   def __init__(self, func, issue_handler):
      super(CoreThread,self).__init__()
      self.func = func
      self.issue_handler = issue_handler
      self.killed = False

   def start_with_traces(self):
      self.__run_backup = self.run 
      self.run = self.__run       
      threading.Thread.start(self) 

   def start(self):      
      threading.Thread.start(self) 

   def __run(self): 
      sys.settrace(self.globaltrace) 
      self.__run_backup() 
      self.run = self.__run_backup

   def run(self):
      try:
         self.func()
      except HistoryInputException as e:
         #self.errorQueue.put(str(e))
         pass
      except LayerSessionAbort:
         pass
      except Exception as e:
         with self.issue_handler.create_issue('Unexpected exception in CoreThread', e) as issue:
            self.issue_handler.put_error(issue.frontend_message)
            log.error(issue.internal_message)
            sentry_sdk.capture_message(str(e))

   def globaltrace(self, frame, event, arg): 
      if event == 'call': 
         return self.localtrace 
      else: 
         return None
   
   def localtrace(self, frame, event, arg): 
      if self.killed: 
         if event == 'line': 
            raise SystemExit() 
      return self.localtrace 
   
   def kill(self): 
      self.killed = True


