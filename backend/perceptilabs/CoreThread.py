import logging
import threading
import traceback
import sys
import sentry_sdk
from sentry_sdk import utils
from sentry_sdk import capture_exception
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


class CoreThread(threading.Thread):
   def __init__(self, func, issue_handler, on_finished):
      super(CoreThread,self).__init__()
      self.func = func
      self.issue_handler = issue_handler
      self.killed = False
      self._on_finished = on_finished

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
      except Exception as e:
         with self.issue_handler.create_issue('Unexpected exception in CoreThread', e) as issue:
            # self.issue_handler.put_error(issue.frontend_message)
            logger.error(issue.internal_message)
            sentry_sdk.capture_message(str(e))
         failed = True
      else:
         failed = False
      finally:
         self._on_finished(failed)
            
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


