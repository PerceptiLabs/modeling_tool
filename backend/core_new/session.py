import time
import copy
import logging

from core_new.api import ApiCallbackHandler
from core_new.api import Api, UiApi, DataApi

log = logging.getLogger(__name__)


class LayerSessionStop(Exception):
    pass


class LayerSession(ApiCallbackHandler):
    PAUSE_TIME = 0.3
    
    def __init__(self, layer_id, code, global_vars=None, local_vars=None,
                 data_container=None, process_handler=None):
        
        self._layer_id = layer_id
        self._code = code
        self._data_container = data_container

        self._stopped = False
        self._paused = False

        self._globals = copy.copy(global_vars) if global_vars is not None else {}
        self._locals = copy.copy(local_vars) if local_vars is not None else {}

        self._process_handler = process_handler

        data_api = DataApi(self)
        ui_api = UiApi(self)
        self._api = Api(data_api, ui_api)

    def run(self):
        if 'api' in self._globals and self._globals['api'] is not self._api:
            log.warning("Overwriting existing, non-identical, api in globals")
            
        self._globals['api'] = self._api        
        exec(self._code, self._globals, self._locals)
        
    def on_store_value(self, name, value):
        if self._data_container is not None:
            self._data_container.store_value(self._layer_id, name, value)

    def on_stack_value(self, name, value):
        if self._data_container is not None:        
            self._data_container.stack_value(self._layer_id, name, value)        

    def on_render(self, dashboard=None):
        if self._process_handler is None:
            return

        while self._paused and not self._stopped:
            time.sleep(self.PAUSE_TIME) # Wait for core to request an unpause or stop.
            self._process_handler.on_process(self, dashboard)            
            
        if self._stopped:
            raise LayerSessionStop

        self._process_handler.on_process(self, dashboard)

    def pause(self):
        if self._process_handler is None:
            raise RuntimeError("process_handler must be set to support pausing")
            
        self._paused = True

    def unpause(self):
        if self._process_handler is None:
            raise RuntimeError("process_handler must be set to support unpausing")
        
        self._paused = False

    def stop(self):
        if self._process_handler is None:
            raise RuntimeError("process_handler must be set to support stopping")
        
        self._stopped = True

    @property
    def is_paused(self):
        return self._paused
        
    @property
    def locals(self):
        return copy.copy(self._locals)
    
    @property
    def globals(self):
        return copy.copy(self._globals)

    @property
    def code(self):
        return self._code

    @property
    def layer_id(self):
        return self._layer_id

    
    
