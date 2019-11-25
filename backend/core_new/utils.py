import tensorflow as tf
from tensorflow.python.eager.context import context, EAGER_MODE, GRAPH_MODE

def set_tensorflow_mode(mode):
    #Hack to turn eager mode on and off so it does not affect the computational core (since eager mode is global) (can be a problem if running when core already is started?)

    if mode not in ['eager', 'graph']:
        raise ValueError("Unknown tensorflow execution mode '{}'".format(mode))
    
    
    tf_version = tf.version.VERSION
    
    if tf_version.startswith('1.15'):
        
        if mode == 'eager':
            tf.enable_eager_execution()
        if mode == 'graph':
            tf.disable_eager_execution()
            
    elif tf_version.startswith('1.13'):
    
        ctx = context()._eager_context
        
        if mode == 'eager':
            ctx.mode = EAGER_MODE
            ctx.is_eager = True
        elif mode == 'graph':
            ctx.mode = GRAPH_MODE        
            ctx.is_eager = False



    
class LoopHook:
    def __init__(self, iterable, max_iter=None, on_create=None, on_iterated=None, on_destroy=None):
        self._iterable = iterable

        self._max_iter = max_iter
        self._on_create = on_create
        self._on_iterated = on_iterated
        self._on_destroy = on_destroy
        
    def __iter__(self):
        if self._on_create:
            self._on_create(self._max_iter)        
        
        for counter, value in enumerate(self._iterable):
            yield value
            
            if self._on_iterated:
                self._on_iterated(counter)

        if self._on_destroy:
            self._on_destroy()
