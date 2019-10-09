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

        
class UiApi:
    def __init__(self, callback_handler):
        self.__handler = callback_handler

    def render(self, dashboard=None):
        self.__handler.on_render(dashboard)

        
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

    @property
    def data(self):
        return self.__data

    @property
    def ui(self):
        return self.__ui

    @property
    def cache(self):
        return self.__cache

    

