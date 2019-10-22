from core_new.cache import SessionCache
from core_new.session import LayerIo

class HistoryInputException(Exception):
    """ Used to not run a layer if there are no inputs """
    pass

class SessionHistory:
    def __init__(self):
        self.reset()

    def reset(self):
        self._sessions = {}
        self._cache = SessionCache()

    def __contains__(self, id_):
        return id_ in self._sessions
        
    def __setitem__(self, id_, value):
        self._sessions[id_] = value

    def items(self):
        for id_, session in self._sessions.items():
            yield id_, session

    def merge_session_outputs(self, layer_ids):
        local_vars = {}
        global_vars = {}

        if not set(layer_ids).issubset(self._sessions):
            diff = set(layer_ids) - set(self._sessions)
            message = "No history available for layers {}. Histories are available for layers {}".format(', '.join(diff), self._sessions.keys())
            raise ValueError(message)
        
        if len(layer_ids) == 1:
            session = self._sessions[layer_ids[0]]
            if session.outputs is None:
                raise HistoryInputException("The input to this layer has not yet been computed")
            locals_=session.outputs.locals
            locals_.pop('X', None)
            locals_ = {'X': locals_}
            local_vars.update(locals_)
            global_vars.update(session.outputs.globals) 
            locals_={'X':''}
                   
        elif len(layer_ids) > 1:
            for id_ in layer_ids:
                session = self._sessions[id_]   
                if session.outputs is None:
                    raise HistoryInputException("The input to this layer has not yet been computed")
                locals_= session.outputs.locals 
                locals_.pop('X',None)      
                local_vars[id_] = locals_
                global_vars.update(session.outputs.globals) # WARNING: may lead to race condition where global variables are updated depending on which layer is executed first.
            local_vars = {'X': local_vars}

    
        outputs = LayerIo(global_vars, local_vars)
        return outputs

    @property
    def cache(self):
        return self._cache
