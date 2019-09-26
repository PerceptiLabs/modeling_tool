import threading
import traceback
import sys
from sentry_sdk import capture_exception
from sentry_sdk import configure_scope

class CoreThread(threading.Thread):
   def __init__(self, func, warningQueue, errorQueue, commandQ, resultQ, network):
      super(CoreThread,self).__init__()
      # threading.Thread.__init__(self)
      self.func=func
      self.warningQueue=warningQueue  #Reports warnings from the core
      self.errorQueue=errorQueue  #Reports errors from the core
      self.resultQ=resultQ  #The queue where the results will come in from
      self.commandQ=commandQ  #The Queue where we can give stop or pause commands to the thread
      self.network=network
   def run(self):
      try:
         self.func(self.warningQueue,self.errorQueue,self.commandQ,self.resultQ,self.network)
      except Exception as e:
         print("--------------------------------")
         #ErrorDump with exact details
         print(traceback.format_exc())
         print("--------------------------------")
         # print(traceback.TracebackException(*sys.exc_info()).stack)


         # tbObj=traceback.TracebackException(*sys.exc_info())
         # while 1:
         #    for i in traceback.walk_tb(tbObj.exc_traceback):
         #       print("********************************")
         #       print(i)
         #       print(i[0].f_locals)
         #    tbObj=tbObj.__context__
         #    if tbObj is None:
         #       break
         
         # print(tbObj.__context__.stack)
         # for i in nformat(tbObj):
         #    print(i)

         # for i in traceback.walk_tb(sys.exc_info()[2]):
         #    for j in traceback.walk_stack(i[0]):
         #       print(j)

         # tb = sys.exc_info()[2]
         # print(sys.exc_info())
         # while tb:
         #    print(sys.stderr)
         #    print('Locals: ', tb.tb_frame.f_locals)
         #    # print >>sys.stderr, 'Globals:', tb.tb_frame.f_globals
         #    tb = tb.tb_next
            

         # del tb
         # print(traceback.format_exception(*sys.exc_info()))

         # print("!!!!!!!!!!!!!!!!!!!!!!!!!!Extract tb: ", traceback.extract_tb(tb))
         # print("!!!!!!!!!!!!!!!!!!!!!!!!!!Extract stack: ", traceback.extract_stack())

         # tb = sys.exc_info()[2]
         # while 1:
         #    if not tb.tb_next:
         #          break
         #    tb = tb.tb_next
         # stack = []
         # f = tb.tb_frame
         # while f:
         #    stack.append(f)
         #    f = f.f_back
         # stack.reverse()
         # print("Locals by frame, innermost last")
         # for frame in stack:
         #    print("********************************************************************")
         #    print("Frame %s in %s at line %s" % (frame.f_code.co_name,frame.f_code.co_filename,frame.f_lineno))
         #    for key, value in frame.f_locals.items():
         #          print("\t%20s = " % key)
         #          # We have to be VERY careful not to cause a new error in our error
         #          # printer! Calling str(  ) on an unknown object could cause an
         #          # error we don't want, so we must use try/except to catch it --
         #          # we can't stop it from happening, but we can and should
         #          # stop it from propagating if it does happen!
         #          try:
         #             print(value)
         #          except:
         #             print("<ERROR WHILE PRINTING VALUE>")


         # tb = sys.exc_info()[2]
         # tb=tb.tb_next
         # while tb is not None:
         #    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Locals: ", tb.tb_frame.f_locals)
         #    tb=tb.tb_next
         # print(tb)
         # print(tb.tb_next.tb_frame.f_locals)
         with configure_scope() as scope:
            scope.set_extra("network",self.network)
            # tb = sys.exc_info()[2]
            # for key,value in tb.tb_next.tb_frame.f_locals.items():
            #    scope.set_extra(key,value)

         #    @scope.add_event_processor
         #    def _(event, hint):
         #       for key,value in tb.tb_next.tb_frame.f_locals.items():
         #          event[key] = value
         #          return event

            # scope.set_extra("warningQueue",self.warningQueue.queue)
            # scope.set_extra("errorQueue",self.errorQueue.queue)
            # 


         capture_exception()
         self.errorQueue.put(str(e))
   def join(self, timeout=None):
      self.commandQ.put("Stop")
      super(CoreThread, self).join(timeout)