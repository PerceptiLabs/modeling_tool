""" Thin classes with private variables to block user access to core """

class ApiCallbackHandler:
    def on_store_value(self, name, value):
        raise NotImplementedError

    def on_stack_value(self, name, value):
        raise NotImplementedError        
    
    def on_render(self, dashboard):
        raise NotImplementedError
    
    
class DataApi:
    def __init__(self, callback_handler):
        self.__handler = callback_handler

    def store(self, **kwargs):
        for name, value in kwargs.items():        
            self.__handler.on_store_value(name, value)

    def stack(self, **kwargs):
        for name, value in kwargs.items():
            self.__handler.on_stack_value(name, value)

        
class UiApi:
    def __init__(self, callback_handler):
        self.__handler = callback_handler

    def render(self, dashboard=None):
        self.__handler.on_render(dashboard)
        

class Api:
    def __init__(self, data, ui):
        self.__data = data
        self.__ui = ui

    @property
    def data(self):
        return self.__data

    @property
    def ui(self):
        return self.__ui


    

