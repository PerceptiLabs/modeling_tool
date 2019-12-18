import threading
import traceback
import sys
# from sentry_sdk import capture_exception
# from sentry_sdk import configure_scope
import logging
from core_new.history import HistoryInputException

log = logging.getLogger(__name__)

class CoreThread(threading.Thread):
   def __init__(self, func, errorQueue):
      super(CoreThread,self).__init__()
      self.func=func
      self.errorQueue=errorQueue
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
         self.errorQueue.put(str(e))
      except:
         # capture_exception()         
         log.exception("Unexpected exception in CoreThread")
         self.errorQueue.put("Internal error in CoreThread!")

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