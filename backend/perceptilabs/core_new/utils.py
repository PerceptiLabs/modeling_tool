import tensorflow as tf
from tensorflow.python.eager.context import context, EAGER_MODE, GRAPH_MODE
from enum import Enum
import collections
import platform
import ntpath, posixpath

TracebackFrame = collections.namedtuple(
    'TracebackFrame', ['lineno', 'name', 'filename', 'line'], module=__name__
)

class YieldLevel(Enum):
    #STOP = 0
    DEFAULT = 1
    SNAPSHOT = 2
    

class Picklable:
    pass


class Picklable:
    pass


def set_tensorflow_mode(mode):
    #Hack to turn eager mode on and off so it does not affect the computational core (since eager mode is global) (can be a problem if running when core already is started?)

    if mode not in ['eager', 'graph']:
        raise ValueError("Unknown tensorflow execution mode '{}'".format(mode))
    
    
    tf_version = tf.version.VERSION
    if tf_version.startswith('1.15'):
        
        if mode == 'eager':
            config = tf.ConfigProto()
            config.gpu_options.allow_growth = True
            tf.enable_eager_execution(config)
        if mode == 'graph':
            tf.disable_eager_execution()
            
    elif tf_version.startswith('1.13'):
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
    
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


def find_free_port(count=1):
    """Find free port(s) and then close. WARNING: this approach is subject to race conditions!"""
    import socket

    sockets = []
    for _ in range(count):
        s = socket.socket()
        s.bind(('', 0)) # Bind to a free port
        sockets.append(s)
        
    ports = []
    for s in sockets:
        ports.append(s.getsockname()[1])
        s.close()
        
    if len(ports) == 1:
        return ports[0]
    else:
        return tuple(ports)    
        


def get_correct_path(path):
    current_platform = platform.system()
    if current_platform == 'Windows':
        new_path = path.replace(posixpath.sep, ntpath.sep)
    elif current_platform == 'Linux' or current_platform == 'Darwin':
        new_path = path.replace(ntpath.sep, posixpath.sep)
    return new_path
