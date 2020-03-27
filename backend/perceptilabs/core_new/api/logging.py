from logging import Handler

class CoreHandler(Handler):
    def emit(self, record):
        # TODO: pass these to an event bus
        pass
