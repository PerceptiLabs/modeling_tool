""" Thin classes with private variables to block user access to core """

from abc import ABC, abstractmethod


class ApiCallbackHandler(ABC):
    @abstractmethod
    def on_store_value(self, name, value):
        raise NotImplementedError
    
    @abstractmethod
    def on_stack_value(self, name, value):
        raise NotImplementedError
    
    @abstractmethod    
    def on_render(self, dashboard):
        raise NotImplementedError
    
    
class DataApi:
    def __init__(self, callback_handler):
        self.__handler = callback_handler

    def store(self, **kwargs):
        for name, value in kwargs.items():        
            self.__handler.on_store_value(name, value)

    def store_locals(self, locals_):
        self.__handler.on_store_locals(locals_)
    
    def store_session(self, sess):
        self.__handler.on_store_session("sess", sess)

    def stack(self, **kwargs):
        for name, value in kwargs.items():
            self.__handler.on_stack_value(name, value)

    def setSaver(self, sess, saver):
        self.__handler.on_set_saver(sess, saver)

    def get_tensors(self):
        return self.__handler.on_tensors_get()

        
class UiApi:
    def __init__(self, callback_handler):
        self.__handler = callback_handler

    def render(self, dashboard=None):
        self.__handler.on_render(dashboard)

    @property
    def headless(self):
        return self.__handler._headless

    @property
    def skip(self):
        return self.__handler._skip

    @skip.setter
    def skip(self, value):
        self.__handler._skip = value

        
class CacheApi:
    def __init__(self, session):
        self.__session = session

    def put(self, key, value):
        self.__session.on_cache_put(key, value)
        
    def get(self, key):
        return self.__session.on_cache_get(key)

    def __contains__(self, key):
        return self.__session.on_cache_contains(key)
        

class Api:
    def __init__(self, session):
        self.__data = DataApi(session)
        self.__ui = UiApi(session)
        self.__cache = CacheApi(session)
        self.__session = session

    @property
    def data(self):
        return self.__data

    @property
    def ui(self):
        return self.__ui

    @property
    def cache(self):
        return self.__cache

    def override_layer_id(self, new_layer_id, func):

        def new_func(*args, **kwargs):
            old_layer_id = self.__session._layer_id
            self.__session._layer_id = new_layer_id
            
            ret_value = func(*args, **kwargs)

            self.__session._layer_id = old_layer_id            
            return ret_value
        
        return new_func
