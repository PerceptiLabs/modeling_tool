import time
import copy
import logging
import functools

from core_new.api import ApiCallbackHandler, Api
from analytics.scraper import get_scraper

log = logging.getLogger(__name__)
scraper = get_scraper()

class LayerSessionStop(Exception):
    """ Used to break out of userland code when stop is pressed in the UI """
    pass


def requires_process_handler(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if args[0]._process_handler is None:
            raise RuntimeError("'{}' requires process_handler to be set!".format(f.__name__))
        return f(*args, **kwargs)
    return wrapper


class LayerIo:
    def __init__(self, global_vars=None, local_vars=None):
        self._globals = copy.copy(global_vars) if global_vars is not None else {}
        self._locals = copy.copy(local_vars) if local_vars is not None else {}

    @property
    def globals(self):
        return copy.copy(self._globals)
    
    @property
    def locals(self):
        return copy.copy(self._locals)


class LayerSession(ApiCallbackHandler):
    PAUSE_TIME = 0.3
    
    def __init__(self, layer_id, layer_type, code, global_vars=None, local_vars=None,
                 data_container=None, process_handler=None, cache=None):        
        self._layer_id = layer_id
        self._layer_type = layer_type
        self._code = code
        self._data_container = data_container
        self._cache = cache

        self._stopped = False
        self._paused = False
        self._headless = False
        self._skip = False
        self._inputs = LayerIo(global_vars, local_vars)
        self._outputs = None

        self._process_handler = process_handler
        self._api = Api(self)

    def run(self):
        global_vars, local_vars = self._get_input_vars(insert_api=True)
        
        exec(self._code, global_vars, local_vars)

        for name, value in local_vars.items():
            self._data_container.store_value(self._layer_id, name, value)

        self._set_output_vars(global_vars, local_vars)

    def _set_output_vars(self, global_vars, local_vars):
        global_out, local_out = {}, {}
        
        for name, value in global_vars.items():
            if name in global_out and value is global_out[name]:
                continue
            global_out[name] = value
                
        for name, value in local_vars.items():
            if name in local_out and value is local_out[name]:
                continue
            local_out[name] = value

        self._outputs = LayerIo(global_out, local_out)

    def _get_input_vars(self, insert_api=True):
        global_vars = self._inputs.globals
        local_vars = self._inputs.locals

        if insert_api and 'api' in global_vars and global_vars['api'] is not self._api:
            log.warning("Overwriting existing, non-identical, api in globals")
        if insert_api:
            global_vars['api'] = self._api

        return global_vars, local_vars
        
    def on_store_value(self, name, value):
        if self._data_container is not None:
            self._data_container.store_value(self._layer_id, name, value)

    def on_store_session(self, name, value):
        if self._data_container is not None:
            self._data_container.store_value_in_root(name, value)

    def on_stack_value(self, name, value):
        if self._data_container is not None:        
            self._data_container.stack_value(self._layer_id, name, value)      

    def on_store_locals(self, locals_):
        for name, value in locals_.items():
            self.on_store_value(name, value)  

    def on_tensors_get(self):
        return self._data_container.on_tensors_get()

    def on_set_saver(self, sess, saver):
        if self._data_container is not None:
            self._data_container.store_value_in_root("saver", (sess, saver))

    @scraper.monitor(tag='session_on_render')
    def on_render(self, dashboard=None):
        if self._process_handler is None:
            return

        while self._paused and not self._stopped:
            time.sleep(self.PAUSE_TIME) # Wait for request to unpause or stop.
            self._process_handler.on_process(self, dashboard)            
            
        if self._stopped:
            log.info("Core has been stopped")
            raise LayerSessionStop

        self._process_handler.on_process(self, dashboard)

    def on_cache_put(self, key, value):
        if self._cache is not None:
            self._cache.put(key, value, self._layer_id)

    def on_cache_get(self, key):
        if self._cache is not None:
            return self._cache.get(key)

    def on_cache_contains(self, key):
        if self._cache is not None:
            return key in self._cache
        else:
            return False

    @requires_process_handler
    def pause(self):
        self._paused = True

    @requires_process_handler        
    def unpause(self):
        self._paused = False

    @requires_process_handler        
    def stop(self):
        self._stopped = True

    @requires_process_handler
    def headlessOn(self):
        self._headless = True

    @requires_process_handler
    def headlessOff(self):
        self._headless = False

    @property
    def is_paused(self):
        return self._paused
        
    @property
    def code(self):
        return self._code

    @property
    def layer_id(self):
        return self._layer_id

    @property
    def layer_type(self):
        return self._layer_type

    @property
    def inputs(self):
        return self._inputs
    
    @property
    def outputs(self):
        return self._outputs
    


if __name__ == "__main__":

    ls = LayerSession(123, 'DataData', 'print("Hello")\n', )
    ls.pause()
